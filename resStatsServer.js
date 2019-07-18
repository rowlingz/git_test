function getFeedData(feedInfo) {
    let feedData = {
        userId: feedInfo.user_id,//作者Id
        pubTime: feedInfo.timestamp,// 发布时间
        commentCount: feedInfo.comment_count,//评论数
        likeCount: feedInfo.like_count,//点赞数
        playCount: feedInfo.view_count,// 浏览量
        text: feedInfo.caption,//配文
        coverUrl: feedInfo.cover_thumbnail_urls[1].url,//封面图url
    };

    let {photoId} = querystring.parse(feedInfo.share_info);
    feedData.detailUrl = `http://m.gifshow.com/fw/photo/${photoId}`;

    let type = feedInfo.main_mv_urls;
    if (type) {
        feedData.feedType = 'mv';
        feedData.videoUrl = type[1].url;
    } else {
        feedData.feedType = 'pictures';
        let picList = feedInfo.ext_params.atlas.list
        feedData.pics = picList.map(function (item){
            return 'http://tx2.a.yximgs.com' + item;
        });
    }
    return feedData;
}

async function handleAppraisal(session, oRep) {
    let {photoInfos} = querystring.parse(session.req.body);
    let feedId = photoInfos.match(/"photoId":"([0-9]+)","/)[1];
    console.log('feedId: ', feedId);
    try {
        let { photos } = JSON.parse(session.res.body);
        let photoInfo = photos[0];
        let evaData = getFeedData(photoInfo);
        evaData.itemId = feedId;

        let reqData = {
            uid: `${feedId}|10`,
            platform: 'KUAISHOU',
            jobType: 'APPRAISAL',
            data: evaData
        };

        console.log('senddata: ', reqData);
        logger.info('senddata: ', reqData);
        await api.finish(reqData);
    } catch (err) {
        logger.error(err);
        await api.finish({
            uid: `${feedId}|10`,
            isErr: true
        });
    }
}

async function handleUser(session, oRep) {
    let {user} = querystring.parse(session.req.body);
    console.log('user: ', user);
    try {
        let { userProfile } = JSON.parse(session.res.body);
        let userData = {
            mid: user,//用户id
            describe: userProfile.profile.user_text,// 签名
            gender: _parseGender(userProfile.profile.user_sex),// 性别（"F" / "M"）
            nickName: userProfile.profile.user_name,//昵称
            verify: userProfile.profile.verified ? '已认证' : '未认证',// false  or true 这里要修改一下 认证情况
            fansNum: userProfile.ownerCount.fan,//粉丝数
            follows: userProfile.ownerCount.follow,//关注数
            notes: userProfile.ownerCount.photo,//作品数量
            likeNum: userProfile.ownerCount.like,//博主点赞别人作品数
            collected: userProfile.ownerCount.collect,//博主收藏别人作品数     
            constellation: userinfo.constellation,//星座
            location: userProfile.cityName//所在地
        };

        let reqData = {
            uid: `${user}|1`,
            platform: 'KUAISHOU',
            jobType: 'USER',
            data: userData,
            tasks: [
                {url: `kwai://profile/${user}`, jobType:5, platform:8}
            ]
        };

        console.log('senddata', reqData)
        //解析数据写入日志文件；
        // logger.info('senddata', reqData);
        // 调用whistle_manage 进行数据回传
        await api.finish(reqData);
    } catch (err) {
        console.log(err);
        await api.finish({
            uid: `${user}|1`,
            isErr: true
        });
    }
}

async function handleFeeds(session, oRep) {
    // 获取时间维度在近90天的数据,如果当前网页的最后一条数据在90天内时间范围，则需继续滑；
    // 如果已经超过了，则将这个url 解析完了，就不滑了，
    let { user_id } = querystring.parse(session.req.body);
    console.log('user_id: ', user_id);

    try {
        let { feeds } = JSON.parse(session.res.body);
        // 终点判断
        let isEndpage;
        let feedDatas;
        if (feeds.length == 0) {
            isEndpage = true;
            feedDatas = [];
            console.log('当前用户无作品');
        } else {
            if (feeds.length < 20) {
                console.log('当前用户已经滑到最后一页');
                isEndpage = true;
            } else {
                let new_time = Date.now();
                // let endFeed = feeds[feeds.length-1];
                // let endTime = (endFeed && endFeed.timestamp) || Date.now();
                let end_time = feeds[feeds.length-1].timestamp;
                if ((new_time - end_time) > 90*24*3600*1000) {
                    console.log('时间差已经大于90天');
                    isEndpage = true;
                } else {
                    isEndpage = false;
                    console.log('时间差小于90天，需要滑动屏幕');
                }
            }

            feedDatas = feeds.map(function (feed) {
                let feedExg = feed.serverExpTag;
                let feedId = feedExg.split('|')[1];
                let feedData = getFeedData(feed);
                feedData.itemId = feedId;
                return feedData;
            });  
        }

        let repData = {
            uid: `${user_id}|5`,
            platform: 'KUAISHOU',
            jobType: 'FEEDS',
            data: feedDatas,
            isEndpage
        }
        console.log('feed长度： ',feedDatas.length);
        console.log({user_id, feedDatas:feedDatas[0]});
        // logger.info('feedsData', respData);
        // 调用api进行数据回传
        await api.feeds(repData);
    } catch (err) {
        console.log(err);
        await api.feeds({
            uid: `${user_id}|5`,
            isErr: true
        });
    }
};