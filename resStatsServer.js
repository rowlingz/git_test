function getUser(session, oRep) {
    try {
        let {user} = JSON.parse(session.res.body);
        let userData = {
            fansNum: user.userProfile.ownerCount.fan,
            followNum:user.userProfile.ownerCount.follow,
            photoNums: user.userProfile.ownerCount.photo_public,
            cityName: user.userProfile.cityName,
            constellation:user.userProfile.constellation,
            userName: user.userProfile.profile.user_name,
            verified:user.userProfile.profile.verified,
            sex: user.userProfile.profile.user_sex,
            text: user.userProfile.profile.user_text
        };

        let repData = {
            uid: user.userProfile.profile.use_id,
            kwaiId: user.userProfile.profile.kwaiId,    //没有的话怎么办？
            platform: 'KUAISHOU',
            jabType: 'USER',
            data: userData,
            tasks: []
        };

        // todo....
    } catch (err) {
        // todo...
    }  
}
