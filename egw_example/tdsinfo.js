var tdsInfo = (function () {

    function localIP(fnCallback) {
        var myPeerConnection = window.RTCPeerConnection || window.mozRTCPeerConnection || window.webkitRTCPeerConnection; //compatibility for firefox and chrome
        var pc = new myPeerConnection({iceServers: []}),
            noop = function() {},
            localIPs = {},
            ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/g,
            key;

        function ipIterate(ip) {
            if (!localIPs[ip]) fnCallback(ip);
            localIPs[ip] = true;
        }

        pc.createDataChannel("");
        pc.createOffer(function(sdp) {
            sdp.sdp.split('\n').forEach(function(line) {
                if (line.indexOf('candidate') < 0) return;
                line.match(ipRegex).forEach(ipIterate);
            });
            pc.setLocalDescription(sdp, noop, noop);
        }, noop);
        pc.onicecandidate = function(ice) {
            if (!ice || !ice.candidate || !ice.candidate.candidate || !ice.candidate.candidate.match(ipRegex)) return;
            ice.candidate.candidate.match(ipRegex).forEach(ipIterate);
        };
    }

    var rs = {
        'browserJavaEnabled':navigator.javaEnabled(),
        'browserCookieEnabled':navigator.cookieEnabled,
        'browserUserAgent':window.navigator.userAgent,
        'platform':window.navigator.platform,
        'browserColorDepth':screen.colorDepth,
        'browserLanguage' : navigator.languages && navigator.languages[0] || // Chrome / Firefox
               navigator.language ||   // All browsers
               navigator.userLanguage, // IE <= 10
        'browserTZ':(new Date()).getTimezoneOffset(),
        'browserTZoffset':(new Date()).getTimezoneOffset()/60
    };

    function localIpCallback(ip) {
        console.log('got ip: ', ip);
        rs['localIP'] = ip;
    }
    // get local IP
    localIP(localIpCallback);

    //IE
    if(!window.innerWidth) {
        if( !(document.documentElement.clientWidth == 0) ) {
            //strict mode
            rs['browserScreenWidth'] = document.documentElement.clientWidth;rs['browserScreenHeight'] = document.documentElement.clientHeight;
        } else{
            //quirks mode
            rs['browserScreenWidth'] = document.body.clientWidth;rs['browserScreenHeight'] = document.body.clientHeight;
        }
    } else {
        //w3c
        rs['browserScreenWidth'] = window.innerWidth;rs['browserScreenHeight'] = window.innerHeight;
    }

    function additionalInfo(rs) {
        var version, osversion, os,osversion,
            bit, mobile, ua = window.navigator.userAgent;
        var platform = navigator.platform;
        if(/MSIE/.test(ua) ) {
            rs['browser']='Internet Explorer';        
            if(/IEMobile/.test(ua)) {
                mobile = 1;
            }
            version = /MSIE \d+[.]\d+/.exec(ua)[0].split(' ')[1];
        } else if(/Chrome/.test(ua)) {
            // Platform override for Chromebooks
            if(/CrOS/.test(ua)) {
                platform = 'CrOS';
            }
            rs['browser']='Chrome';
            version = /Chrome\/[\d\.]+/.exec(ua)[0].split('/')[1];        
        } else if( /Opera/.test(ua) ) {
            rs['browser']='Opera';
            if( /mini/.test(ua) || /Mobile/.test(ua) ) {
                mobile = 1;
            }
        } else if( /Android/.test(ua) ) {        
            rs['browser']='Android Webkit Browser';
            mobile = 1;
            os = /Android\s[\.\d]+/.exec(ua)[0];
        } else if( /Firefox/.test(ua) ) {        
            rs['browser']='Firefox';
            if( /Fennec/.test(ua) ) {
                mobile = 1;
            }
            version = /Firefox\/[\.\d]+/.exec(ua)[0].split('/')[1];
        } else if( /Safari/.test(ua) ) {
            rs['browser']='Safari';
            if( (/iPhone/.test(ua)) || (/iPad/.test(ua)) || (/iPod/.test(ua)) ) {
                os = 'iOS';
                mobile = 1;
            }
        }

        if(!version){
            version = /Version\/[\.\d]+/.exec(ua);
            if(version) {
                version = version[0].split('/')[1];
            } else {
                version = /Opera\/[\.\d]+/.exec(ua)[0].split('/')[1];
            }
        }

        if( platform === 'MacIntel' || platform === 'MacPPC' ) {
            os = 'Mac OS X';
            osversion = /10[\.\_\d]+/.exec(ua)[0];
            if( /[\_]/.test(osversion) ) {
                osversion = osversion.split('_').join('.');
            }
        } else if ( platform === 'CrOS' ) {
            os = 'ChromeOS';
        } else if ( platform === 'Win32' || platform == 'Win64' ) {
            os = 'Windows';
            bit = platform.replace(/[^0-9]+/,'');
        } else if ( !os && /Android/.test(ua) ) {
            os = 'Android';
        } else if ( !os && /Linux/.test(platform) ) {
            os = 'Linux';
        } else if ( !os && /Windows/.test(ua) ) {
            os = 'Windows';
        }

        rs['browserVersion'] = version;
        rs['osVersion'] = osversion;
        rs['osBit'] = bit;
        rs['os'] = os;
        rs['mobile'] = mobile;
        rs['appCodeName'] = navigator.appCodeName;
        rs['appName'] = navigator.appName;
        rs['product'] = navigator.product;
    };
    
    additionalInfo(rs);

    function addClientInfoTestData(rs) {
        var billAddr = {
            "billAddrCity":"Bill City Name",
            "billAddrCountry":"840",
            "billAddrLine1":"Bill Address Line 1",
            "billAddrLine2":"Bill Address Line 2",
            "billAddrLine3":"Bill Address Line 3",
            "billAddrPostCode":"Bill Post Code",
            "billAddrState":"CO"
        };
        
        rs['billAddr'] = billAddr;

        var shipAddr = {
            "shipAddrCity":"Ship City Name",
            "shipAddrCountry":"840",
            "shipAddrLine1":"Ship Address Line 1",
            "shipAddrLine2":"Ship Address Line 2",
            "shipAddrLine3":"Ship Address Line 3",
            "shipAddrPostCode":"Ship Post Code",
            "shipAddrState":"CO"
        };

        rs['shipAddr'] = shipAddr;

        var merchantRiskIndicator = {
            "shipIndicator":"02",
            "deliveryTimeframe":"01",
            "deliveryEmailAddress":"deliver@email.com",
            "reorderItemsInd":"01",
            "preOrderPurchaseInd":"02",
            "preOrderDate":"20170519",
            "giftCardAmount":"337",
            "giftCardCurr":"840",
            "giftCardCount":"02"
        };

        rs['merchantRiskIndicator'] = merchantRiskIndicator;

        var acctInfo = {
            "acctType":"03",
            "acctID":"personal account",
            "chAccAgeInd":"03",
            "chAccDate":"20140328",
            "chAccChangeInd":"04",
            "chAccChange":"20160712",
            "chAccPwChangeInd":"02",
            "chAccPwChange":"20170328",
            "shipAddressUsageInd":"04",
            "shipAddressUsage":"20160714",
            "txnActivityDay":"1",
            "txnActivityYear":"21",
            "provisionAttemptsDay":"0",
            "nbPurchaseAccount":"11",
            "suspiciousAccActivity":"01",
            "shipNameIndicator":"02",
            "paymentAccInd":"04",
            "paymentAccAge":"20160917"
        };

        rs['acctInfo'] = acctInfo;

        rs['addrMatch'] = "Y";
        rs['threeDSRequestorAuthenticationInfo'] = "AUTH_INFO";
        rs['threeDSRequestorPriorAuthenticationInfo'] = "PRIOR_AUTH_I";
        rs['messageExtension'] = "messageExtension";
        rs['threeDSRequestorChallengeInd'] = "01";
        rs['threeDSRequestorAuthenticationInd'] = "04";
        rs['threeDSRequestorURL'] = "https://threeDSRequestorURL.com";
        
        //var recipientNspkFunds = {
        //    "destAcctNum":"1234567890123456789",
        //};
        
        //rs['recipientNspkFunds'] = recipientNspkFunds;
    };

    addClientInfoTestData(rs);

    console.log(JSON.stringify(rs));

    var Base64={_keyStr:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",encode:function(e){var t="";var n,r,i,s,o,u,a;var f=0;e=Base64._utf8_encode(e);while(f<e.length){n=e.charCodeAt(f++);r=e.charCodeAt(f++);i=e.charCodeAt(f++);s=n>>2;o=(n&3)<<4|r>>4;u=(r&15)<<2|i>>6;a=i&63;if(isNaN(r)){u=a=64}else if(isNaN(i)){a=64}t=t+this._keyStr.charAt(s)+this._keyStr.charAt(o)+this._keyStr.charAt(u)+this._keyStr.charAt(a)}return t},decode:function(e){var t="";var n,r,i;var s,o,u,a;var f=0;e=e.replace(/[^A-Za-z0-9\+\/\=]/g,"");while(f<e.length){s=this._keyStr.indexOf(e.charAt(f++));o=this._keyStr.indexOf(e.charAt(f++));u=this._keyStr.indexOf(e.charAt(f++));a=this._keyStr.indexOf(e.charAt(f++));n=s<<2|o>>4;r=(o&15)<<4|u>>2;i=(u&3)<<6|a;t=t+String.fromCharCode(n);if(u!=64){t=t+String.fromCharCode(r)}if(a!=64){t=t+String.fromCharCode(i)}}t=Base64._utf8_decode(t);return t},_utf8_encode:function(e){e=e.replace(/\r\n/g,"\n");var t="";for(var n=0;n<e.length;n++){var r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r)}else if(r>127&&r<2048){t+=String.fromCharCode(r>>6|192);t+=String.fromCharCode(r&63|128)}else{t+=String.fromCharCode(r>>12|224);t+=String.fromCharCode(r>>6&63|128);t+=String.fromCharCode(r&63|128)}}return t},_utf8_decode:function(e){var t="";var n=0;var r=c1=c2=0;while(n<e.length){r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r);n++}else if(r>191&&r<224){c2=e.charCodeAt(n+1);t+=String.fromCharCode((r&31)<<6|c2&63);n+=2}else{c2=e.charCodeAt(n+1);c3=e.charCodeAt(n+2);t+=String.fromCharCode((r&15)<<12|(c2&63)<<6|c3&63);n+=3}}return t}}
    return Base64.encode(JSON.stringify(rs));

})();
