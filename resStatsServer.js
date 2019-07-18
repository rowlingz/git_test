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
        // logger.info('senddata: ', reqData);
        await api.finish(reqData);
    } catch (err) {
        logger.error(err);
        await api.finish({
            uid: `${feedId}|10`,
            isErr: true
        });
    }
}