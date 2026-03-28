function loadScript(url, callback) {
  var script = document.createElement("script");
  script.type = "text/javascript";
  script.src = url;

  if (script.readyState) {
    // IE
    script.onreadystatechange = function () {
      if (script.readyState == "loaded" || script.readyState == "complete") {
        script.onreadystatechange = null;
        callback && callback();
      }
    };
  } else {
    // Other browsers
    script.onload = function () {
      callback && callback();
    };
  }

  document.getElementsByTagName("head")[0].appendChild(script);
}
/**
 * 跨项目通用组件
 */
(function (g, factory) {
  var isHideCaptcha =
    window.location.href.indexOf("live") >= 0 &&
    window.location.href.indexOf("/m") >= 0;
  if (!isHideCaptcha) {
    loadScript("https://turing.captcha.qcloud.com/TCaptcha.js");
  }
  if (typeof exports === "object") {
    module.exports = factory();
  } else {
    g.MxCommonComp = factory();
  }
})(this, function () {
  var host = getHost();
  // 弹窗类型切换renderType
  var isTab;
  var qr_login_positon;
  // 轮训次数
  var pollingTime = 0;
  var totalTimes = 6;

  var staticUrl =
    host.mainsite === "https://www.shixiseng.com" ||
    host.frontend === "https://www.shixiseng.com"
      ? "https://sxsimg.xiaoyuanzhao.com/static_common/common-comp/"
      : "https://dev-static-sxs.oss-cn-hangzhou.aliyuncs.com/static_common/common-comp/";
  var isTv = window.location.host.indexOf("live") >= 0;
  var _qrCode =
    "https://sxsimg.xiaoyuanzhao.com/static_common/common-comp/login/popup/loading.gif";
  var _loading =
    "https://sxsimg.xiaoyuanzhao.com/static_common/common-comp/login/popup/loading.gif";
  var EventBus = createEventBus();
  var scanSucQueue = []; // 用作存储扫码成功的回调
  var scanBeforeSucQueue = []; // 用作存储扫码成功之前的回调
  var scanGuideType;
  var resetDom = function () {
    var dx_login = document.querySelectorAll(".form-title__type")[0];
    var mm_login = document.querySelectorAll(".form-title__type")[1];
    var scan_code = document.querySelector(".login-type-tab");
    var scan_login = document.querySelector(".login-qipao-tab");
    var loginMain = document.querySelector(".form-title");
    var agreement = document.querySelector(".agreement");
    var icon1 = document.querySelector(".icon1");
    var icon2 = document.querySelector(".icon2");
    var auth_text = document.querySelector(".auth-text");
    var formFooter = document.querySelector(".form-footer");
    var enterprise = document.querySelector(".enterprise");
    dx_login.style.display = "inline-block";
    icon1.style.display = "inline-block";
    icon2.style.display = "inline-block";
    agreement.style.display = "block";
    mm_login.style.marginLeft = "0";
    loginMain.style.paddingTop = "0";
    formFooter.style.paddingTop = "0";
    removeClass(scan_code, "hide");
    removeClass(scan_login, "hide");
    removeClass(icon1, "hide");
    removeClass(icon2, "hide");
    addClass(enterprise, "hide");
    removeClass(auth_text, "hide");
  };

  fetchAreaCode();
  // fetchVerifyCode()
  // 生成根据时间戳生成UUID保证唯一性
  var uuId = generateUUID(); // 全局缓存变量uuId
  var env = window.location.host.split("-")[0];
  ajax("get", host.newApiHost + "/api/account/v3.0/baseinfo", {
    success: function (res) {
      var env = window.location.host.split("-")[0];
      if (res.code === 101 || JSON.stringify(res.msg) === "{}") {
        getQrCode(true);
      }

      var liveHost = "http://" + env + "-live-frontend.mshare.cn";
      var liveLineHost = "https://live.shixiseng.com";
      var mainSiteHost = "http://" + env + "-sxs-frontend.mshare.cn";
      var mainSiteWebHost = "http://" + env + "-sxs-web.mshare.cn";
      var mainSiteLineHost = "https://www.shixiseng.com";
      var minSiteXz = "https://resume.shixiseng.com";
      var showMessagePathName = [
        "/xiaozhao",
        "/resume/",
        "/review/",
        "/personal-center",
        "/intern/",
        "/interns",
      ];
      var minSiteUrl = [
        liveHost,
        liveLineHost,
        minSiteXz,
        mainSiteHost,
        mainSiteLineHost,
        mainSiteWebHost,
      ];
      const isshow = showMessagePathName.some(function (path) {
        return (
          window.location.href.indexOf(path) >= 0 &&
          window.location.href.indexOf("/m/") === -1
        );
      });
      const isShowUrl = minSiteUrl.some(function (path) {
        return (
          window.location.href === path || window.location.href === path + "/"
        );
      });
      if (
        window.location.host === env + "-local.mshare.cn:8700" ||
        window.location.host === env + "-local.mshare.cn" ||
        isShowUrl ||
        isshow
      ) {
        var url = "";
        if (env === "sit1" || env === "sit2" || env === "uat") {
          url =
            "https://dev-static-sxs.oss-cn-hangzhou.aliyuncs.com/static_common/";
        } else {
          url = "https://sxsimg.xiaoyuanzhao.com/static_common/";
        }

        loadScript(url + "sidebar-global/index.js", function () {
          var msg = new window.MessageModule(res, getHost, ajax);

          setTimeout(function () {
            msg.renderDom();
          }, 0);
        });
      }
    },
  });

  function getCookie(name) {
    var arr;
    var reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");
    if ((arr = document.cookie.match(reg))) {
      return unescape(arr[2]);
    } else {
      return null;
    }
  }

  // sxs domain
  function isSxsWeb() {
    var l = location.hostname;
    return l.match(/shixiseng.com|mshare.cn/);
  }

  //set token only dialog plugin
  function setToken(token) {
    if (token) {
      localStorage.setItem("sxsToken", token);
    }
  }

  function FooterLogin(options) {
    var _this = this;
    options = options || {};
    render(options.el);

    _this.loginFormPhoneEl =
      _this.el.getElementsByClassName("login-form--phone")[0];
    _this.closeEl = _this.el.getElementsByClassName("footer-login__close")[0];

    _this.closeEl.addEventListener("click", function () {
      setCookie("bottom_banner", true, 6 * 60 * 60 * 1000);
      _this.hide();
    });

    _this.hide = function () {
      removeClass(_this.el, "footer-login--is-show");
      if (options.hide && isFunction(options.hide)) {
        options.hide();
      }
    };

    _this.show = function () {
      if (isTv) {
        resetDom();
      }
      addClass(_this.el, "footer-login--is-show");
    };
    // loadQrcode()

    function setCookie(cname, cvalue, expiresDate) {
      var d = new Date();
      d.setTime(d.getTime() + expiresDate);
      var expires = "expires=" + d.toGMTString();
      var cookieDomain = getDomain(location.host);
      document.cookie =
        cname +
        "=" +
        cvalue +
        "; " +
        expires +
        (cookieDomain ? ";Domain=" + cookieDomain : "") +
        ";Path=/";
    }

    function getDomain(host) {
      if (host.match(/kongzhongtalk\.cn/)) {
        // 临时
        return "kongzhongtalk.cn";
      } else if (host.match(/msharetest\.cn/)) {
        return "msharetest.cn";
      } else if (host.match(/mshare\.cn/)) {
        return "mshare.cn";
      } else if (host.match(/shixiseng\.com/)) {
        return "shixiseng.com";
      }
    }

    _this.el
      .getElementsByClassName("a3")[0]
      .addEventListener("click", function () {
        if (window.xMethod) {
          window.xMethod.sendData({
            event_type: "login",
            event_id: "web_1000006",
          });
        }
        window.location.href = getHost().mainsite + "/user/sso/weibo/auth";
      });
    _this.el
      .getElementsByClassName("a4")[0]
      .addEventListener("click", function () {
        if (window.xMethod) {
          window.xMethod.sendData(
            {
              event_type: "login",
              event_id: "web_1000005",
            },
            function () {
              // ajax('get', host.newApiHost + '/api/account/v3.0/pc/qq/auth_url', {
              //   success: function(res) {
              //     if (res.code === 100) {
              //       window.location.href = res.msg
              //     }
              //   }
              // })
              window.location.href = getHost().mainsite + "/user/sso/qq/auth";
            }
          );
        }
      });

    function render(el) {
      if (el) {
        _this.el = el;
      } else {
        _this.el = document.createElement("div");
        document.body.appendChild(_this.el);
      }
      addClass(_this.el, "footer-login");
      _this.el.innerHTML =
        '<div class="footer-login__content">\
         <div class="footer-login__img"></div>\
         <div class="footer-login__right">\
           <div class="qrcode-wrap">\
             <div class="qrcode-box">\
               <img class="qrcode loading" src="' +
        _qrCode +
        '" alt="" />\
             </div>\
             <div class="qrcode-text fq1 hide">已扫码</div>\
             <div class="qrcode-text fq2 hide">等待确认登录</div>\
             <div class="resetCode hide">\
               <div class="tip">二维码已过期</div>\
               <div class="btn">重新获取</div>\
             </div>\
           </div>\
           <div class="other-wrap">\
             <div class="icon"><img src="' +
        staticUrl +
        "login/bottom/qipao.png" +
        '" alt=""/></div>\
             <div class="content">\
               <a href="#"\
                 title="使用短信登录"\
                 class="item a1" data-sa="click" data-sname="30"\
                 data-sevent="land_click" data-desc="index-短信登录">\
                 <span class="text">短信登录</span>\
               </a>\
               <a href="#"\
                 title="使用密码登录"\
                 class="item a2" data-sa="click" data-sname="31"\
                 data-sevent="land_click" data-desc="index-密码登录">\
                 <span class="text">密码登录</span>\
               </a>\
               <a\
                 title="使用新浪微博账号登录" class="item a3" data-sa="click" data-sname="32"\
                 data-starget="/user/sso/weibo/auth" data-sevent="land_click"\
                 data-desc="index-微博登录">\
                 <span class="text">微博登录</span>\
               </a>\
               <a\
                 title="使用腾讯QQ账号登录"\
                 class="item a4" data-sa="click" data-sname="33"\
                 data-starget="/user/sso/qq/auth" data-sevent="land_click"\
                 data-desc="index-QQ登录">\
                 <span class="text">QQ登录</span>\
               </a>\
             </div>\
           </div>\
         </div>\
         <img class="footer-login__close" src="' +
        staticUrl +
        "login/bottom/icon_close.png" +
        '" alt=""/>\
       </div>';
    }
  }

  function generateUUID() {
    var d = new Date().getTime();
    if (window.performance && typeof window.performance.now === "function") {
      d += performance.now(); //use high-precision timer if available
    }
    var uuid = "xxxxxxx4xxyxxxxx".replace(/[xy]/g, function (c) {
      var r = (d + Math.random() * 16) % 16 | 0;
      d = Math.floor(d / 16);
      return (c == "x" ? r : (r & 0x3) | 0x8).toString(16);
    });
    return uuid;
  }

  function loadLoading() {
    if (document.getElementById("qrcode")) {
      document.getElementById("qrcode").src = _loading;
      addClass(document.getElementById("qrcode"), "loading");
      removeClass(
        document.querySelector(".qrcode-content .qrcode-box"),
        "noBorder"
      );
    }
    if (document.querySelector(".login__row--1 .qrcode-wrap .qrcode")) {
      document.querySelector(".login__row--1 .qrcode-wrap .qrcode").src =
        _loading;
      addClass(
        document.querySelector(".login__row--1 .qrcode-wrap .qrcode"),
        "loading"
      );
      removeClass(
        document.querySelector(".login__row--1 .qrcode-wrap .qrcode-box"),
        "noBorder"
      );
    }
    if (document.querySelector(".footer-login__right .qrcode-wrap .qrcode")) {
      document.querySelector(".footer-login__right .qrcode-wrap .qrcode").src =
        _loading;
      addClass(
        document.querySelector(".footer-login__right .qrcode-wrap .qrcode"),
        "loading"
      );
      removeClass(
        document.querySelector(".footer-login__right .qrcode-wrap .qrcode-box"),
        "noBorder"
      );
    }
  }

  function loadQrcode() {
    if (document.getElementById("qrcode")) {
      document.getElementById("qrcode").src = _qrCode;
    }
    if (document.querySelector(".login__row--1 .qrcode-wrap .qrcode")) {
      document.querySelector(".login__row--1 .qrcode-wrap .qrcode").src =
        _qrCode;
    }
    if (document.querySelector(".footer-login__right .qrcode-wrap .qrcode")) {
      document.querySelector(".footer-login__right .qrcode-wrap .qrcode").src =
        _qrCode;
    }
  }

  function removeLoading() {
    if (document.getElementById("qrcode")) {
      removeClass(document.getElementById("qrcode"), "loading");
      document.getElementById("qrcode").src = _qrCode;
      addClass(
        document.querySelector(".qrcode-content .qrcode-box"),
        "noBorder"
      );
    }
    if (document.querySelector(".login__row--1 .qrcode-wrap .qrcode")) {
      removeClass(
        document.querySelector(".login__row--1 .qrcode-wrap .qrcode"),
        "loading"
      );
      addClass(
        document.querySelector(".login__row--1 .qrcode-wrap .qrcode-box"),
        "noBorder"
      );
      document.querySelector(".login__row--1 .qrcode-wrap .qrcode").src =
        _qrCode;
    }
    if (document.querySelector(".footer-login__right .qrcode-wrap .qrcode")) {
      removeClass(
        document.querySelector(".footer-login__right .qrcode-wrap .qrcode"),
        "loading"
      );
      addClass(
        document.querySelector(".footer-login__right .qrcode-wrap .qrcode-box"),
        "noBorder"
      );
      document.querySelector(".footer-login__right .qrcode-wrap .qrcode").src =
        _qrCode;
    }
  }

  function asyncloadQrcode() {
    if (
      document.getElementsByClassName("resetCode") &&
      document.getElementById("qrcode")
    ) {
      removeLoading();
    } else {
      setTimeout(function () {
        asyncloadQrcode();
      }, 500);
    }
  }

  function getQrCode(first) {
    // 针对好僧项目 小程序需要做判断；关注好奇僧域名变化有新增
    var url = location.hostname;
    var isUni = url.match(/haoqi|university|career/);
    var typeStr = isUni ? "_uni" : "";
    if (!first) {
      loadLoading();
    }
    pollingTime = 0;
    ajax(
      "get",
      host.newApiHost +
        "/api/account/v3.0/mina/create/minacode/v2?scene=" +
        uuId +
        typeStr +
        "&pages=pages/login/pcloginpage/pcloginpage&stype=common&utm_source=" +
        getCookie("utm_source") +
        "&utm_campaign=" +
        getCookie("utm_campaign"),
      {
        success: function (res) {
          if (res && res.code === 100) {
            _qrCode = "data:image/png;base64," + res.msg;
            if (first) {
              asyncloadQrcode();
            } else {
              removeLoading();
            }
            getPolling();
          } else {
            pollingTime = totalTimes;
            if (first) {
              asyncloadQrcode();
            } else {
              removeLoading();
            }
            renderResetCode();
          }
        },
        error: function (err) {
          pollingTime = totalTimes;
          if (first) {
            asyncloadQrcode();
          } else {
            removeLoading();
          }
          renderResetCode();
        },
      }
    );
    // return host.newApiHost + '/api/account/v2.0/create/minacode?pages=pages/login/pcloginpage/pcloginpage&scene=' + uuId + '&stype=common'
  }
  function getPolling() {
    localStorage.removeItem("sxsToken");
    ajax("post", host.newApiHost + "/api/account/v2.0/mina/polling", {
      params: {
        scene: uuId,
      },
      success: function (res) {
        pollingTime++;
        setToken(res.token);
        if (res.code == 100 && res.msg.isLogin) {
          // location.replace(host.mainsite);
          if (window.xMethod) {
            var positon = "弹窗";
            if (qr_login_positon == "popup") {
              positon = "弹窗";
            } else {
              if (window.location.pathname === "/") {
                positon = "头部";
              } else {
                positon = "通栏";
              }
            }
            window.xMethod.sendData({
              event_type: "login",
              event_id: "web_1000020",
              ext_value: positon,
            });
          }
          var scanBeforeSuc =
            scanBeforeSucQueue.length && scanBeforeSucQueue.shift();
          if (scanSucQueue.length > 0) {
            var scanCallback = scanSucQueue.shift();
            getGuideProcess(scanCallback, function () {
              if (scanGuideType === 2) {
                if (scanBeforeSuc) {
                  document.querySelector(".login-dialog-wrap") &&
                    removeClass(
                      document.querySelector(".login-dialog-wrap"),
                      "login-dialog-wrap--is-show"
                    );
                  scanBeforeSuc(function () {
                    scanCallback();
                  });
                }
                // 可扩展其他定制登录成功回调
              } else if (scanGuideType === 1) {
                if (window.location.pathname === "/user/login") {
                  window.location.replace(
                    host.frontend + "/guide?next=" + getNextUrlParam("next") ||
                      ""
                  );
                } else {
                  window.location.replace(
                    host.frontend +
                      "/guide?t=" +
                      (!isSxsWeb() ? localStorage.getItem("sxsToken") : "") +
                      "&next=" +
                      location.href
                  );
                }
              } else {
                scanCallback();
              }
            });
          } else {
            var defaultScanCallBack = function () {
              if (window.location.pathname === "/user/login") {
                window.location.replace(
                  host.frontend + "/guide?next=" + getNextUrlParam("next") || ""
                );
              } else {
                window.location.reload();
              }
            };
            getGuideProcess(defaultScanCallBack, function () {
              if (scanGuideType === 2) {
                if (scanBeforeSuc) {
                  document.querySelector(".login-dialog-wrap") &&
                    removeClass(
                      document.querySelector(".login-dialog-wrap"),
                      "login-dialog-wrap--is-show"
                    );
                  scanBeforeSuc(function () {
                    defaultScanCallBack();
                  });
                }
                // 可扩展其他定制登录成功回调
              } else if (scanGuideType === 1) {
                window.location.replace(host.frontend + "/guide");
              } else {
                defaultScanCallBack();
              }
            });
          }
        } else {
          if (res.code == 500 && res.msg.isScan) {
            var qrcodeText = document.querySelectorAll(".qrcode-text");
            for (var i = 0; i < qrcodeText.length; i++) {
              removeClass(qrcodeText[i], "hide");
            }
            addOpacity();
          }
          if (pollingTime < totalTimes) {
            getPolling();
          } else {
            renderResetCode();
          }
        }
      },
      error: function () {
        pollingTime++;
      },
    });
  }

  function getGuideProcess(onLoginSuccess, callback) {
    ajax("get", host.newApiHost + "/api/account/v3.0/pc/user/guide", {
      success: function (res) {
        if (res.code === 100) {
          if (window.xMethod) {
            window.xMethod.sendData({
              event_type: "login",
              event_id: "web_1000019",
            });
          }
          if (res.msg.is_complete) {
            //  已完善登录成功后上报用户信息给datafinder
            // if (window.xMethod) {
            //   window.xMethod.dataFinderUserInfo();
            // }
            onLoginSuccess(res);
          } else {
            // 新用户创建一个新简历，然后跳引导页
            callback();
          }
        } else {
          if (window.xMethod) {
            window.xMethod.sendData({
              event_type: "login",
              event_id: "web_1000019",
              ext_value: res.msg,
            });
          }
          showAlert({
            type: "error",
            message: res.msg,
          });
        }
      },
    });
  }

  function getNextUrlParam(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象

    var r = window.location.search.substr(1).match(reg); //匹配目标参数

    // if (r != null) return unescape(r[2]);
    if (r != null) return decodeURIComponent(r[2]);
    return ""; //返回参数值
  }

  function addOpacity() {
    if (document.getElementById("qrcode")) {
      if (_qrCode === _loading) {
        addClass(document.getElementById("qrcode"), "hide");
      }
      addClass(document.getElementById("qrcode"), "opacity");
    }
    if (document.querySelector(".login__row--1 .qrcode-wrap .qrcode")) {
      if (_qrCode === _loading) {
        addClass(
          document.querySelector(".login__row--1 .qrcode-wrap .qrcode"),
          "hide"
        );
      }
      addClass(
        document.querySelector(".login__row--1 .qrcode-wrap .qrcode"),
        "opacity"
      );
    }
    if (document.querySelector(".footer-login__right .qrcode-wrap .qrcode")) {
      if (_qrCode === _loading) {
        addClass(
          document.querySelector(".footer-login__right .qrcode-wrap .qrcode"),
          "hide"
        );
      }
      addClass(
        document.querySelector(".footer-login__right .qrcode-wrap .qrcode"),
        "opacity"
      );
    }
  }

  function removeOpacity() {
    removeClass(document.getElementById("qrcode"), "opacity");
    if (hasClass(document.getElementById("qrcode"), "hide")) {
      removeClass(document.getElementById("qrcode"), "hide");
    }
    var qrcodes = document.querySelectorAll(".qrcode-wrap .qrcode");
    for (var j = 0; j < qrcodes.length; j++) {
      removeClass(qrcodes[j], "opacity");
      if (hasClass(qrcodes[j], "hide")) {
        removeClass(qrcodes[j], "hide");
      }
    }
  }

  function renderResetCode() {
    var resetCode = document.getElementsByClassName("resetCode");
    if (resetCode && document.getElementById("qrcode")) {
      for (var i = 0; i < resetCode.length; i++) {
        removeClass(resetCode[i], "hide");
      }
      addOpacity();
      var qrcodeText = document.querySelectorAll(".qrcode-text");
      for (var i = 0; i < qrcodeText.length; i++) {
        addClass(qrcodeText[i], "hide");
      }
      removeLoading();
    } else {
      setTimeout(function () {
        renderResetCode();
      }, 500);
    }
  }

  function observe(value, callback) {
    if (!value || typeof value !== "object") {
      return;
    }
    Object.keys(value).forEach(function (key) {
      defineReactive(value, key, value[key], callback);
    });
  }

  function defineReactive(obj, key, val, callback) {
    observe(val, callback);
    Object.defineProperty(obj, key, {
      get: function () {
        return val;
      },
      set: function (newVal) {
        if (newVal === val) {
          return;
        }
        val = newVal;
        callback();
      },
    });
  }

  function LoginDialog(options) {
    var _this = this;
    options = options || {};

    options.guideType = options.guideType || 3;
    options.loginSuccessCallBack = options.loginSuccessCallBack || null;

    render(options.el);

    _this.loginPanelEl = _this.el.getElementsByClassName("login-panel")[0];
    _this.closeEl = _this.el.getElementsByClassName("login-dialog__close")[0];
    _this.options = options;

    _this.LoginPanel = new LoginPanel({
      el: _this.loginPanelEl,
      onLoginSuccess: options.onLoginSuccess,
      guideType: _this.options.guideType || 3, // 注册引导类型 1.展示默认注册引导 2.展示留学生标记弹窗 3.不需要注册引导
      loginSuccessCallBack: options.loginSuccessCallBack,
      transformFormData: options.transformFormData,
    });

    observe(_this.options, function () {
      _this.LoginPanel = new LoginPanel({
        el: _this.loginPanelEl,
        onLoginSuccess: _this.options.onLoginSuccess,
        guideType: _this.options.guideType || 3, // 注册引导类型 1.展示默认注册引导 2.展示留学生标记弹窗 3.不需要注册引导
        loginSuccessCallBack: _this.options.loginSuccessCallBack,
        transformFormData: _this.options.transformFormData,
      });
    });

    _this.el.addEventListener("click", function (e) {
      if (e.target === _this.el) {
        _this.hide();
      }
    });

    _this.closeEl.addEventListener("click", function () {
      _this.hide();
    });

    _this.show = function (type, isPwd) {
      if (isTv) {
        resetDom();
      }

      addClass(_this.el, "login-dialog-wrap--is-show");
      document.body.style.overflow = "hidden";
      qr_login_positon = "popup";
      isTab = type == "other" ? true : false;
      var imgTabBtn = _this.el.getElementsByClassName("login-type-tab")[0];
      var imgQipaoBtn = _this.el.getElementsByClassName("login-qipao-tab")[0];
      renderType(isTab, imgTabBtn, imgQipaoBtn);
      if (isPwd) {
        if (document.all) {
          _this.el.getElementsByClassName("form-title__type")[1].click();
        } else {
          var e = document.createEvent("MouseEvents");
          e.initEvent("click", true, true);
          _this.el
            .getElementsByClassName("form-title__type")[1]
            .dispatchEvent(e);
        }
      } else if (isTab && !isPwd) {
        if (document.all) {
          _this.el.getElementsByClassName("form-title__type")[0].click();
        } else {
          var e = document.createEvent("MouseEvents");
          e.initEvent("click", true, true);
          _this.el
            .getElementsByClassName("form-title__type")[0]
            .dispatchEvent(e);
        }
      } else if (!isTab && !isTab) {
        if (
          !hasClass(
            _this.loginPanelEl.getElementsByClassName("resetCode")[0],
            "hide"
          )
        ) {
          // 优化处理
          getResetCode();
        }
      }

      // tv下显示hr的tip
      addClass(_this.el.getElementsByClassName("hr_tip")[0], "hidden");
      if (isTv) {
        var icon_hr = _this.el.getElementsByClassName("icon3");
        for (var hindex = 0; hindex < icon_hr.length; hindex++) {
          var isStudy = icon_hr[hindex].getAttribute("data-info") === "study";
          if (isStudy) {
            addClass(icon_hr[hindex], "hide");
          } else {
            removeClass(icon_hr[hindex], "hide");
          }
        }
      }
    };

    _this.clear = function () {
      pollingTime = 0;
    };

    _this.hide = function () {
      removeClass(_this.el, "login-dialog-wrap--is-show");
      document.body.style.overflow = null;
      qr_login_positon = "";
    };

    if (document.querySelector(".footer-login__right .a1")) {
      document
        .querySelector(".footer-login__right .a1")
        .addEventListener("click", function () {
          _this.show("other");
        });
      document
        .querySelector(".footer-login__right .a2")
        .addEventListener("click", function () {
          _this.show("other", true);
        });
    }

    function render(el) {
      if (el || _this.el) {
        _this.el = el;
      } else {
        _this.el = document.createElement("div");
        document.body.appendChild(_this.el);
      }
      addClass(_this.el, "login-dialog-wrap");
      _this.el.innerHTML =
        '<div class="login-dialog">\
         <i class="iconfont iconguanbi login-dialog__close"></i>\
         <div class="login-panel"></div>\
       </div>';
    }
  }
  // 弹窗切换渲染
  function renderType(isTab, el, el_qipao, type) {
    if (isTab) {
      el.setAttribute(
        "src",
        staticUrl + "login/popup/icon_login_qr_normal.png"
      );
      el_qipao.setAttribute("src", staticUrl + "login/popup/qipao_qrcode.png");
      addClass(document.querySelector(".login-panel__content.qrcode"), "hide");
      removeClass(
        document.querySelector(".login-panel__content.other"),
        "hide"
      );
      if (isTv) {
        if (type) {
          return;
        }
        var login_icon = document.querySelectorAll(".icon3");
        for (var i = 0; i < login_icon.length; i++) {
          if (login_icon[i].getAttribute("data-info") === "study") {
            removeClass(login_icon[i], "hide");
          } else {
            addClass(login_icon[i], "hide");
          }
        }
      }
    } else {
      el.setAttribute(
        "src",
        staticUrl + "login/popup/icon_login_sms_normal.png"
      );
      el_qipao.setAttribute("src", staticUrl + "login/popup/qipao_sms.png");
      addClass(document.querySelector(".login-panel__content.other"), "hide");
      removeClass(
        document.querySelector(".login-panel__content.qrcode"),
        "hide"
      );
      if (window.xMethod) {
        window.xMethod.sendData({
          event_type: "login",
          event_id: "web_1000004",
        });
      }

      if (isTv) {
        var login_icon = document.querySelectorAll(".icon3");
        for (var i = 0; i < login_icon.length; i++) {
          if (login_icon[i].getAttribute("data-info") === "study") {
            addClass(login_icon[i], "hide");
          } else {
            removeClass(login_icon[i], "hide");
          }
        }
      }
    }
  }

  function getResetCode() {
    uuId = generateUUID();
    getQrCode();
    removeOpacity();
    var resetCode = document.getElementsByClassName("resetCode");
    for (var j = 0; j < resetCode.length; j++) {
      addClass(resetCode[j], "hide");
    }
  }

  function getUrlParam(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); // 构造一个含有目标参数的正则表达式对象

    var r = window.location.search.substr(1).match(reg); // 匹配目标参数

    // if (r != null) return unescape(r[2]);
    if (r != null) return decodeURIComponent(r[2]);
    return ""; // 返回参数值
  }

  function LoginPanel(options) {
    var _this = this;
    var encodedURI;
    var src = window.location.href;
    if (src.indexOf("deloitte") > -1) {
      src = getUrlParam("next") || "/";
      encodedURI = encodeURIComponent(src);
    } else {
      encodedURI = encodeURIComponent(window.location);
    }
    options.guideType = options.guideType || 3;
    _this.options = options;
    // 若外包引入登录成功方法堆栈方式
    scanSucQueue = [];
    // 扫码成功之前的队列
    scanBeforeSucQueue = [];
    options.onLoginSuccess && scanSucQueue.push(options.onLoginSuccess);
    options.loginSuccessCallBack &&
      scanBeforeSucQueue.push(options.loginSuccessCallBack);
    scanGuideType = _this.options.guideType || 3;

    // 记录登录切换模式
    _this.imgTab =
      '<img class="login-type-tab" src="' +
      staticUrl +
      "login/popup/icon_login_sms_normal.png" +
      '" alt="" />';
    _this.qipaoTab =
      '<img class="login-qipao-tab" src="' +
      staticUrl +
      "login/popup/qipao_sms.png" +
      '" alt="" />';
    // var encodedURI = encodeURIComponent(window.location)
    render(options.el);

    _this.changeTypeBtnEl = _this.el.getElementsByClassName(
      "form-title__change-type"
    )[0];
    _this.formTypeEl1 = _this.el.getElementsByClassName("form-title__type")[0];
    _this.formTypeEl2 = _this.el.getElementsByClassName("form-title__type")[1];

    _this.loginFormPhoneEl =
      _this.el.getElementsByClassName("login-form--phone")[0];
    _this.loginFormPwdEl =
      _this.el.getElementsByClassName("login-form--pwd")[0];
    // _this.agreementEl = _this.el.getElementsByClassName('agreement')[0]
    _this.greementSpan = _this.el.getElementsByClassName("greement_text")[0];
    _this.formFooter = _this.el.getElementsByClassName("form-footer")[0];

    _this.phoneLoginForm = new PhoneLoginForm({
      el: _this.loginFormPhoneEl,
      onLoginSuccess: options.onLoginSuccess,
      guideType: _this.options.guideType, // 注册引导类型 1.展示默认注册引导 2.展示留学生标记弹窗 3.不需要注册引导
      loginSuccessCallBack: options.loginSuccessCallBack, // 登录成功回调之前的操作
      transformFormData: options.transformFormData,
    });
    _this.pwdLoginForm = new PwdLoginForm({
      el: _this.loginFormPwdEl,
      onLoginSuccess: options.onLoginSuccess,
      guideType: _this.options.guideType, // 注册引导类型 1.展示默认注册引导 2.展示留学生标记弹窗 3.不需要注册引导
      loginSuccessCallBack: options.loginSuccessCallBack, // 登录成功回调之前的操作
      transformFormData: options.transformFormData,
    });

    observe(_this.options, function () {
      _this.phoneLoginForm = new PhoneLoginForm({
        el: _this.loginFormPhoneEl,
        onLoginSuccess: _this.options.onLoginSuccess,
        guideType: _this.options.guideType, // 注册引导类型 1.展示默认注册引导 2.展示留学生标记弹窗 3.不需要注册引导
        loginSuccessCallBack: _this.options.loginSuccessCallBack, // 登录成功回调之前的操作
        transformFormData: _this.options.transformFormData,
      });
      _this.pwdLoginForm = new PwdLoginForm({
        el: _this.loginFormPwdEl,
        onLoginSuccess: _this.options.onLoginSuccess,
        guideType: _this.options.guideType, // 注册引导类型 1.展示默认注册引导 2.展示留学生标记弹窗 3.不需要注册引导
        loginSuccessCallBack: _this.options.loginSuccessCallBack, // 登录成功回调之前的操作
        transformFormData: _this.options.transformFormData,
      });
    });

    _this.formTypeEl1.addEventListener("click", function () {
      removeClass(_this.formTypeEl2, "active");
      addClass(_this.formTypeEl1, "active");
      // addClass(_this.agreementEl, 'agreement--is-show')
      addClass(_this.loginFormPhoneEl, "login-form--is-show");
      removeClass(_this.loginFormPwdEl, "login-form--is-show");
      // removeClass(_this.formFooter, 'blank-height')
      _this.greementSpan.innerText = "登录/注册";
      if (window.xMethod) {
        window.xMethod.sendData({
          event_type: "login",
          event_id: "web_1000008",
        });
      }
      if (isTv) {
        var icon_hr = _this.el.getElementsByClassName("icon3");
        for (var hindex = 0; hindex < icon_hr.length; hindex++) {
          if (icon_hr[hindex].getAttribute("data-info") === "study") {
            addClass(icon_hr[hindex], "hide");
          } else {
            removeClass(icon_hr[hindex], "hide");
          }
        }
      }
    });
    _this.formTypeEl2.addEventListener("click", function () {
      // removeClass(_this.agreementEl, 'agreement--is-show')
      removeClass(_this.loginFormPhoneEl, "login-form--is-show");
      addClass(_this.loginFormPwdEl, "login-form--is-show");
      addClass(_this.formTypeEl2, "active");
      removeClass(_this.formTypeEl1, "active");
      // addClass(_this.formFooter, 'blank-height')
      _this.greementSpan.innerText = "登录";
      if (window.xMethod) {
        window.xMethod.sendData({
          event_type: "login",
          event_id: "web_1000007",
        });
      }
      if (isTv) {
        var icon_hr = _this.el.getElementsByClassName("icon3");
        for (var hindex = 0; hindex < icon_hr.length; hindex++) {
          if (icon_hr[hindex].getAttribute("data-info") === "study") {
            addClass(icon_hr[hindex], "hide");
          } else {
            removeClass(icon_hr[hindex], "hide");
          }
        }
      }
    });
    loadQrcode();
    isTab = options.type == "other" ? true : false;
    _this.imgTabBtn = _this.el.getElementsByClassName("login-type-tab")[0];
    _this.qipaoTabBtn = _this.el.getElementsByClassName("login-qipao-tab")[0];
    renderType(isTab, _this.imgTabBtn, _this.qipaoTabBtn);
    _this.imgTabBtn.addEventListener("click", function () {
      isTab = !isTab;
      if (isTv) {
        var icon_hr = _this.el.getElementsByClassName("icon3");
        if (!isTab) {
          for (var hindex = 0; hindex < icon_hr.length; hindex++) {
            removeClass(icon_hr[hindex], "hide");
          }
        } else {
          for (var hindex = 0; hindex < icon_hr.length; hindex++) {
            if (icon_hr[hindex].getAttribute("data-info") === "study") {
              addClass(icon_hr[hindex], "hide");
            } else {
              removeClass(icon_hr[hindex], "hide");
            }
          }
          /* if (hasClass(_this.formTypeEl2, 'active')) {
             for (var hindex = 0; hindex < icon_hr.length; hindex++) {
               addClass(icon_hr[hindex], 'hide');
             }
           } */
        }
      }
      if (!isTab) {
        if (hasClass(document.getElementById("qrcode"), "opacity")) {
          // 优化处理
          getResetCode();
        }
      }
      renderType(isTab, _this.imgTabBtn, _this.qipaoTabBtn, true);
    });
    _this.qipaoTabBtn.addEventListener("click", function () {
      isTab = !isTab;

      if (!isTab) {
        if (hasClass(document.getElementById("qrcode"), "opacity")) {
          // 优化处理
          getResetCode();
        }
      }
      renderType(isTab, _this.imgTabBtn, _this.qipaoTabBtn, true);
    });
    _this.imgTabBtn.addEventListener(
      "mouseover",
      function () {
        if (isTab) {
          _this.imgTabBtn.setAttribute(
            "src",
            staticUrl + "login/popup/icon_login_qr_hover.png"
          );
        } else {
          _this.imgTabBtn.setAttribute(
            "src",
            staticUrl + "login/popup/icon_login_sms_hover.png"
          );
        }
      },
      false
    );
    _this.imgTabBtn.addEventListener(
      "mouseout",
      function () {
        if (isTab) {
          _this.imgTabBtn.setAttribute(
            "src",
            staticUrl + "login/popup/icon_login_qr_normal.png"
          );
        } else {
          _this.imgTabBtn.setAttribute(
            "src",
            staticUrl + "login/popup/icon_login_sms_normal.png"
          );
        }
      },
      false
    );

    var resetCode = document.getElementsByClassName("resetCode");
    for (var i = 0; i < resetCode.length; i++) {
      resetCode[i].addEventListener(
        "click",
        function () {
          getResetCode();
        },
        false
      );
    }
    var weibos = _this.el.getElementsByClassName("icon1");
    for (var windex = 0; windex < weibos.length; windex++) {
      weibos[windex].addEventListener(
        "click",
        function () {
          if (window.xMethod) {
            window.xMethod.sendData({
              event_type: "login",
              event_id: "web_1000006",
            });
          }
          window.location.href =
            "https://www.shixiseng.com/user/sso/weibo/auth?redicturl=" +
            encodedURI;
        },
        false
      );
    }

    var qqs = _this.el.getElementsByClassName("icon2");
    for (var qindex = 0; qindex < qqs.length; qindex++) {
      qqs[qindex].addEventListener(
        "click",
        function () {
          if (window.xMethod) {
            window.xMethod.sendData(
              {
                event_type: "login",
                event_id: "web_1000005",
              },
              function () {
                // ajax('get', host.newApiHost + '/api/account/v3.0/pc/qq/auth_url?redirect_url=' + encodedURI, {
                //   success: function(res) {
                //     if (res.code === 100) {
                //       window.location.href = res.msg
                //     }
                //   }
                // })
                window.location.href =
                  "https://www.shixiseng.com/user/sso/qq/auth?redicturl=" +
                  encodedURI;
              }
            );
          }
        },
        false
      );
    }

    // tv兼容hr
    if (isTv) {
      var icon_hr = _this.el.getElementsByClassName("icon3");
      for (var hindex = 0; hindex < icon_hr.length; hindex++) {
        icon_hr[hindex].addEventListener(
          "click",
          function () {
            /* 4.12.0 start */
            var dx_login = document.querySelectorAll(".form-title__type")[0];
            var mm_login = document.querySelectorAll(".form-title__type")[1];
            var scan_code = document.querySelector(".login-type-tab");
            var scan_login = document.querySelector(".login-qipao-tab");
            var loginMain = document.querySelector(".form-title");
            var resetCode = document.querySelector(".resetCode");
            var isStudy = this.getAttribute("data-info") === "study";
            var agreement = document.querySelector(".agreement");
            var icon1 = document.querySelector(".icon1");
            var icon2 = document.querySelector(".icon2");
            var auth_text = document.querySelector(".auth-text");
            var formFooter = document.querySelector(".form-footer");
            var enterprise = document.querySelector(".enterprise");

            if (isStudy) {
              dx_login.style.display = "inline-block";
              icon1.style.display = "inline-block";
              icon2.style.display = "inline-block";
              agreement.style.display = "block";
              mm_login.style.marginLeft = "0";
              loginMain.style.paddingTop = "0";
              formFooter.style.paddingTop = "0";
              removeClass(scan_code, "hide");
              removeClass(scan_login, "hide");
              removeClass(icon1, "hide");
              removeClass(icon2, "hide");
              addClass(enterprise, "hide");
              removeClass(auth_text, "hide");
              removeClass(this, "hide");

              if (!hasClass(resetCode, "hide")) {
                // 优化处理
                getResetCode();
              }
              isTab = false;
              renderType(isTab, _this.imgTabBtn, scan_login);
            } else {
              dx_login.style.display = "none";
              agreement.style.display = "none";
              icon1.style.display = "none";
              icon2.style.display = "none";
              mm_login.style.marginLeft = "-60%";
              loginMain.style.paddingTop = "42px";
              formFooter.style.paddingTop = "75px";
              removeClass(enterprise, "hide");
              addClass(scan_code, "hide");
              addClass(scan_login, "hide");
              addClass(auth_text, "hide");
              addClass(this, "hide");

              if (document.all) {
                _this.el.getElementsByClassName("form-title__type")[1].click();
              } else {
                var e = document.createEvent("MouseEvents");
                e.initEvent("click", true, true);
                _this.el
                  .getElementsByClassName("form-title__type")[1]
                  .dispatchEvent(e);
              }

              removeClass(
                _this.el.getElementsByClassName("hr_tip")[0],
                "hidden"
              );
              setTimeout(function () {
                addClass(
                  _this.el.getElementsByClassName("hr_tip")[0],
                  "hidden"
                );
              }, 2000);
              isTab = true;
              renderType(isTab, _this.imgTabBtn, _this.qipaoTabBtn);
            }

            /* 4.12.0 end */
          },
          false
        );
      }
    }

    function render(el) {
      _this.el = el;
      var greement_link =
        '<span class="greement_text">登录/注册</span>即代表您同意<a href="' +
        host.mainsite +
        '/rule" class="agreement__link">「实习僧用户协议及隐私政策」</a>';
      _this.el.innerHTML =
        _this.imgTab +
        _this.qipaoTab +
        '<div class="login-panel__content other hide">\
           <div class="form-title">\
             <div class="form-title__type active">短信登录</div>\
             <div class="form-title__type">密码登录</div>\
           </div>\
           <div class="login-form login-form--phone login-form--is-show"></div>\
           <div class="login-form login-form--pwd"></div>\
           <div class="form-footer">\
             <div class="agreement agreement--is-show">' +
        greement_link +
        '</div>\
             <div class="line"></div>\
             <div class="outer-auth">' +
        renderFooter() +
        '</div>\
           </div>\
         </div>\
         <div class="login-panel__content qrcode">\
           <div class="qrcode-title">微信扫一扫，立即登录</div>\
           <div class="qrcode-content">\
             <div class="qrcode-box">\
               <img id="qrcode" src="' +
        _qrCode +
        '" alt="" />\
             </div>\
             <div class="qrcode-text hide">已扫码，等待确认登录</div>\
             <div class="resetCode hide">\
               <div class="tip">二维码已过期</div>\
               <div class="btn">重新获取</div>\
             </div>\
           </div>\
           <div class="form-footer">\
             <div class="agreement agreement--is-show">\
               登录/注册即代表您同意<a href="' +
        host.mainsite +
        '/rule" class="agreement__link">「实习僧用户协议及隐私政策」</a>\
             </div>\
             <div class="line"></div>\
             <div class="outer-auth">' +
        renderFooter() +
        "</div>\
           </div>\
         </div>";
      addClass(_this.el, "login-panel");
    }

    function renderFooter() {
      var str = "";
      str +=
        '<span class="auth-text">其他登录：</span>\
       <a class="outer-auth__item icon1">&nbsp;</a>\
       <a class="outer-auth__item icon2">&nbsp;</a>';
      if (isTv) {
        var url = staticUrl + "login/popup/jt.png";
        str += '<a class="icon3">HR登录<img src=' + url + ' alt=""/></a>';
        str +=
          '<a class="icon3" data-info="study">学生登录<img src=' +
          url +
          ' alt=""/></a>';
      }
      return str;
    }
  }

  function PwdLoginForm(options) {
    var _this = this;
    options = options || {};
    var errMsgInline =
      options.errMsgInline == undefined ? true : options.errMsgInline;
    var submitForm = isFunction(options.submitForm)
      ? options.submitForm
      : defaultSubmitForm;
    var onLoginSuccess = isFunction(options.onLoginSuccess)
      ? options.onLoginSuccess
      : defaultLoginSuccessHandler;
    var loginSuccessCallBack = isFunction(options.loginSuccessCallBack)
      ? options.loginSuccessCallBack
      : "";
    var transformFormData = isFunction(options.transformFormData)
      ? options.transformFormData
      : defaultTransformFormData;
    render(options.el);

    _this.formData = {
      username: "",
      password: "",
      remember_login: false,
    };

    var validators = {
      username: validateUsername,
      password: validatePassword,
    };

    _this.inputWrapEls = {
      username: _this.el.getElementsByClassName("input-wrap--username")[0],
      password: _this.el.getElementsByClassName("input-wrap--password")[0],
    };
    _this.usernameInputEl =
      _this.el.getElementsByClassName("username-input")[0];
    _this.passwordInputEl =
      _this.el.getElementsByClassName("password-input")[0];
    _this.togglePasswordVisibleEl = _this.el.getElementsByClassName(
      "toggle-password-visible"
    )[0];
    _this.loginBtnEl = _this.el.getElementsByClassName("login-btn")[0];

    _this.togglePasswordVisibleEl.addEventListener("click", function () {
      if (hasClass(_this.togglePasswordVisibleEl, "iconmimaguan")) {
        removeClass(_this.togglePasswordVisibleEl, "iconmimaguan");
        addClass(_this.togglePasswordVisibleEl, "iconmimakai");
      } else {
        removeClass(_this.togglePasswordVisibleEl, "iconmimakai");
        addClass(_this.togglePasswordVisibleEl, "iconmimaguan");
      }
      var type = _this.passwordInputEl.getAttribute("type");
      _this.passwordInputEl.setAttribute(
        "type",
        type === "text" ? "password" : "text"
      );
    });

    _this.usernameInputEl.addEventListener("input", function (e) {
      clearError("username");
      _this.formData.username = e.target.value;
    });

    _this.usernameInputEl.addEventListener("blur", function (e) {
      validateUsername();
    });

    _this.passwordInputEl.addEventListener("input", function (e) {
      clearError("password");
      _this.formData.password = e.target.value;
    });

    _this.passwordInputEl.addEventListener("blur", function (e) {
      validatePassword();
    });

    _this.loginBtnEl.addEventListener("click", function () {
      var valid = true;
      Object.keys(validators).forEach(function (key) {
        valid = validators[key]() && valid;
      });
      if (valid) {
        submitForm(_this.formData);
      }
    });

    function defaultSubmitForm(formData) {
      formData = copyFrom({}, transformFormData(formData), true);
      if (isTv) {
        // formData.origin = 'tv'
        if (hasClass(document.querySelector(".login-qipao-tab"), "hide")) {
          formData.allow_company = true;
        } else {
          formData.allow_company = false;
        }
      }

      // TV 走hr的登录接口
      if (isTv && formData.allow_company) {
        var liveLoginData = {};
        liveLoginData.username = formData.username;
        liveLoginData.password = formData.password;
        ajax("post", host.liveApi + "/api/v1/hr/login", {
          contentType: "json",
          data: liveLoginData,
          success: function (res) {
            if (res.code === 100) {
              onLoginSuccess();
            } else {
              showAlert({
                type: "error",
                message: res.msg,
              });
            }
          },
        });
        return;
      }

      // 非TV 用户登录逻辑
      formData.password = myencode(formData.password);
      localStorage.removeItem("sxsToken"); // 登录前 清除一次token
      ajax("post", host.newApiHost + "/api/account/v3.0/login", {
        data: formData,
        success: function (res) {
          setToken(res.token);
          if (res.code === 100) {
            // onLoginSuccess(res)
            getGuideProcess(onLoginSuccess, function () {
              if (window.xMethod) {
                window.xMethod.sendData({
                  event_type: "login",
                  event_id: "web_1000010",
                });
              }
              if (options.guideType === 2) {
                if (loginSuccessCallBack) {
                  // 登录成功之前
                  document.querySelector(".login-dialog-wrap") &&
                    removeClass(
                      document.querySelector(".login-dialog-wrap"),
                      "login-dialog-wrap--is-show"
                    );
                  loginSuccessCallBack(function () {
                    onLoginSuccess();
                  });
                }
              } else if (options.guideType === 1) {
                if (window.location.pathname === "/user/login") {
                  window.location.replace(
                    host.frontend + "/guide?next=" + getNextUrlParam("next") ||
                      ""
                  );
                } else {
                  window.location.replace(
                    host.frontend +
                      "/guide?t=" +
                      (!isSxsWeb() ? localStorage.getItem("sxsToken") : "") +
                      "&next=" +
                      location.href
                  );
                }
              } else {
                onLoginSuccess();
              }
            });
          } else {
            if (window.xMethod) {
              window.xMethod.sendData({
                event_type: "login",
                event_id: "web_1000010",
                ext_value: res.msg,
              });
            }
            showAlert({
              type: "error",
              message: res.msg,
            });
          }
        },
      });
    }

    function validateUsername() {
      var phone_reg = /^[0-9]{3,13}$/;
      var email_reg =
        /^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z]{2,9}$/;
      if (!_this.formData.username) {
        showError("请将登录信息填写完整", "username");
        return false;
      } else {
        if (_this.formData.username.indexOf("@") >= 0) {
          if (!email_reg.test(_this.formData.username)) {
            showError("邮箱格式验证失败，请重新输入");
            return false;
          }
        } else {
          if (!phone_reg.test(_this.formData.username)) {
            showError("手机号输入不正确，请重新输入");
            return false;
          }
        }
      }
      clearError("username");
      return true;
    }

    function validatePassword() {
      if (!_this.formData.password) {
        showError("请将登录信息填写完整", "password");
        return false;
      } else {
        clearError("password");
        return true;
      }
    }

    function clearError(field) {
      if (errMsgInline && field) {
        removeClass(_this.inputWrapEls[field], "input-wrap--is-error");
        _this.inputWrapEls[field].getElementsByClassName(
          "error-msg"
        )[0].innerText = "";
      }
    }

    function showError(msg, field) {
      msg = msg || "";
      if (errMsgInline && field) {
        addClass(_this.inputWrapEls[field], "input-wrap--is-error");
        _this.inputWrapEls[field].getElementsByClassName(
          "error-msg"
        )[0].innerText = msg;
      } else {
        showAlert({
          message: msg,
          type: "error",
        });
      }
    }

    function render(el) {
      var _img =
        '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAaCAYAAACpSkzOAAAAAXNSR0IArs4c6QAAAERlWElmTU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAAAGqADAAQAAAABAAAAGgAAAABMybYKAAAB3UlEQVRIDbVWO07DQBC1LV+Awg2FS+IepXMKkKBNpNwCUlDlEKkoILdACi2RnMLuEL1JmQIKF1wA2by32l3ZDpY/sUeydnZ25j3P7Nc0aiQMw4ssy2amad7A1YV+zhD0v9Ac0N9C30wmkz3tVWJWDYDgEiArjF9X+ZTsAQiXIPwo2UX3iAjgdhRFjxi9g340/h+IsoEog772ff8B+q+ysy0AIYsz2F5AcJV3aquDZIeYObL7UbGWUpgJ9JNJiCd/lFjEFKKJWK4mmTiOY/CrE2LJKRCuonScePTeMVgoZRmMBJ7nCXMcx0aSJGWXQl/O2ZgLRGQEglUdSQGhYYeYxKa7ifRGaZrGDWN12eqyyeMhs5ENkmneWKe3IVBYyGpmgY07vrGg3ga/NkIOzpHbJqijr2shLXF2dQRoFEYOvY8aRXR04jLnHPEUHlq+mdFhaBZycI62QxORw4K8Dk2E6dlYuDs+QRQMSBZg3+3FqgPjkiujbzJiEpu4+rTGCf6EWt73SQaSZ2SzKBCBxMYB+4b2pNtV/ShIdpiWW7TiStcbVhrmdFDOXVuJQSz9btClU6Ays94fJzojRcS/kHUdw9ZmNdKXt+kin4nGVUpVKy/GKYIrH5Dci3KbVMEYf1U300GN6WRSAAAAAElFTkSuQmCC" alt=""/>';
      var tip =
        '<div class="hr_tip hidden"><div class="warn_tip">' +
        _img +
        "</div>HR仅支持“密码登录”或进入HR中心登录噢~</div>";
      _this.el = el;
      var renderContent =
        '<div class="input-wrap input-wrap--username">\
         <div class="input-wrap-icon">\
           <img class="wrap-icon" src="' +
        staticUrl +
        "login/popup/phone.png" +
        '" alt=""/>\
         </div>\
         <input type="text" class="username-input" placeholder="请输入手机号/邮箱" name="username" autocomplete="username">\
         <span class="error-msg">请输入</span>\
       </div>\
       <div class="input-wrap input-wrap--password">\
         <div class="input-wrap-icon">\
           <img class="wrap-icon" src="' +
        staticUrl +
        "login/popup/password.png" +
        '" alt=""/>\
         </div>\
         <input type="password" class="password-input" placeholder="请输入密码" name="password" autocomplete="password">\
         <i class="toggle-password-visible iconfont iconmimaguan"></i>\
         <a class="forget-pwd" style="right:284px">忘记密码？</a>\
         <a class="forget-pwd enterprise hide" data-info="enterprise">企业免费注册</a>\
         <span class="error-msg"></span>\
       </div>\
       <button class="login-btn" type="button">登录</button>';

      _this.el.innerHTML = tip + renderContent;
      addClass(_this.el, "login-form login-form--pwd");
    }
    _this.el.getElementsByClassName("forget-pwd")[0].addEventListener(
      "click",
      function () {
        if (window.xMethod) {
          window.xMethod.sendData({
            event_type: "login",
            event_id: "web_1000009",
          });
        }
        setTimeout(function () {
          if (
            isTv &&
            hasClass(document.querySelector(".login-qipao-tab"), "hide")
          ) {
            window.location.href = host.hrHost + "/find-pass?from=tv";
            return;
          }
          window.location.href = host.frontend + "/find-pass";
        }, 500);
      },
      false
    );
    _this.el.getElementsByClassName("forget-pwd")[1].addEventListener(
      "click",
      function () {
        /* if (window.xMethod) {
         window.xMethod.sendData({
           event_type: 'login',
           event_id: 'web_1000009'
         })
       } */
        setTimeout(function () {
          window.location.href = host.hrHost;
        }, 500);
      },
      false
    );
  }

  function PhoneLoginForm(options) {
    var _this = this;
    options = options || {};
    var errMsgInline =
      options.errMsgInline == undefined ? true : options.errMsgInline;
    var submitForm = isFunction(options.submitForm)
      ? options.submitForm
      : defaultSubmitForm;
    var transformFormData = isFunction(options.transformFormData)
      ? options.transformFormData
      : defaultTransformFormData;
    var onLoginSuccess = isFunction(options.onLoginSuccess)
      ? options.onLoginSuccess
      : defaultLoginSuccessHandler;
    var loginSuccessCallBack = isFunction(options.loginSuccessCallBack)
      ? options.loginSuccessCallBack
      : "";
    render(options.el);

    _this.formData = {
      stype: "pc",
      areaCode: "+86",
    };
    var verifyCountdown = 0;

    var validators = {
      phoneNumber: validatePhoneNumber,
      verifyCode: validateVerifyCode,
    };

    _this.areaCodeEl = _this.el.getElementsByClassName("area-code")[0];
    _this.areaCodeOptionsEl =
      _this.el.getElementsByClassName("area-code-option")[0];
    _this.phoneNumberInputEl =
      _this.el.getElementsByClassName("phone-number-input")[0];
    _this.verifyCodeInputEl =
      _this.el.getElementsByClassName("verify-code-input")[0];
    _this.getVerifyCodeBtnEl = _this.el.getElementsByClassName(
      "get-verify-code-btn"
    )[0];
    _this.verifyCodePanelEl =
      _this.el.getElementsByClassName("verify-code-panel")[0];
    _this.loginBtnEl = _this.el.getElementsByClassName("login-btn")[0];
    _this.inputWrapEls = {
      phoneNumber: _this.el.getElementsByClassName(
        "input-wrap--phone-number"
      )[0],
      verifyCode: _this.el.getElementsByClassName("input-wrap--verify-code")[0],
    };

    _this.areaCodeOptionsPanel = new AreaCodeOptionsPanel({
      el: _this.areaCodeOptionsEl,
    });

    _this.areaCodeOptionsPanel.on(
      "select",
      function (data) {
        _this.areaCodeEl.innerText = data.code;
        _this.formData.areaCode = data.code;
      },
      true
    );

    _this.areaCodeOptionsPanel.on("show", function () {
      addClass(_this.areaCodeEl, "area-code--active");
    });

    _this.areaCodeOptionsPanel.on("hide", function () {
      removeClass(_this.areaCodeEl, "area-code--active");
    });

    _this.phoneNumberInputEl.addEventListener("input", function (e) {
      clearError("phoneNumber");
      _this.formData.tel = _this.phoneNumberInputEl.value;
    });

    _this.phoneNumberInputEl.addEventListener("blur", function () {
      validatePhoneNumber();
    });

    _this.verifyCodeInputEl.addEventListener("input", function (e) {
      clearError("verifyCode");
      _this.formData.rdcode = _this.verifyCodeInputEl.value;
    });

    _this.verifyCodeInputEl.addEventListener("blur", function () {
      validateVerifyCode();
    });

    _this.areaCodeEl.addEventListener("click", function onAreaCodeClick() {
      if (window.xMethod) {
        window.xMethod.sendData({
          event_type: "login",
          event_id: "web_1000011",
        });
      }
      _this.areaCodeOptionsPanel.show();
    });

    _this.getVerifyCodeBtnEl.addEventListener(
      "click",
      function onGetVeriryCodeBtnClick(e) {
        if (verifyCountdown <= 0 && validatePhoneNumber("verify")) {
          if (window.xMethod) {
            window.xMethod.sendData({
              event_type: "login",
              event_id: "web_1000013",
            });
          }
          // _this.verifyCodePanel.show()
          try {
            var captcha1 = new TencentCaptcha("2097478085", function (res) {
              verifySuccess(res);
            });
            captcha1.show();
          } catch (error) {
            showAlert({
              type: "error",
              message: "验证码校验失效，请刷新页面稍后再试",
            });
          }
        }
      }
    );
    _this.loginBtnEl.addEventListener("click", function () {
      var valid = true;
      Object.keys(validators).forEach(function (key) {
        valid = validators[key]() && valid;
      });
      if (valid) {
        submitForm(_this.formData);
      }
    });

    function verifySuccess(res) {
      var data = {
        type: "login",
        randstr: res.randstr,
        ticket: res.ticket,
        tel: _this.formData.tel,
        areaCode: _this.formData.areaCode,
        ssotype: "",
        user_flag: "user",
      };
      ajax("get", host.newApiHost + "/api/account/v3.0/telrandcode/v2", {
        params: data,
        success: function (res) {
          if (res.code === 100) {
            if (window.xMethod) {
              window.xMethod.sendData({
                event_type: "login",
                event_id: "web_1000018",
              });
            }
            _this.formData.rdid = res.msg;

            verifyCountdown = _this.formData.areaCode == "+86" ? 60 : 180;
            _this.getVerifyCodeBtnEl.innerText =
              verifyCountdown + "s后重新获取";
            addClass(_this.getVerifyCodeBtnEl, "get-verify-code-btn__disabled");
            var interval = setInterval(function () {
              verifyCountdown--;
              if (verifyCountdown === 0) {
                _this.getVerifyCodeBtnEl.innerText = "获取验证码";
                removeClass(
                  _this.getVerifyCodeBtnEl,
                  "get-verify-code-btn__disabled"
                );
                clearInterval(interval);
              } else {
                _this.getVerifyCodeBtnEl.innerText =
                  verifyCountdown + "s后重新获取";
                addClass(
                  _this.getVerifyCodeBtnEl,
                  "get-verify-code-btn__disabled"
                );
              }
            }, 1000);
          } else {
            showAlert({
              type: "error",
              message: res.msg,
            });
          }
        },
      });
    }

    function defaultSubmitForm(formData) {
      var postData = {};
      var defaultUtmSource = options.defaultUtmSource || "pc";
      //  var utmSource = document.cookie.match(/utm_source=(.+?);/);
      var utmSource = document.cookie.match(/utm_source_first=(.+?);/); // 注意 注册这里取的utm_source_first
      if (utmSource == null) {
        utmSource = "";
      } else {
        utmSource = utmSource[1];
      }
      postData.utm_source = utmSource || defaultUtmSource;
      postData.stype = "pc";
      copyFrom(postData, transformFormData(formData), true);
      localStorage.removeItem("sxsToken"); // 默认清除一次
      ajax("post", host.newApiHost + "/api/account/v3.0/verification/login", {
        data: copyFrom(postData, transformFormData(formData), true),
        success: function ($res) {
          if ($res.code === 100) {
            setToken($res.token);
            getGuideProcess(onLoginSuccess, function () {
              ajax("post", host.newApiHost + "/api/resume/v2.0/resume/detail", {
                data: {
                  stype: "online",
                },
                contentType: "json",
                success: function (_res) {
                  if (options.guideType === 2) {
                    if (loginSuccessCallBack) {
                      // 登录成功之前
                      document.querySelector(".login-dialog-wrap") &&
                        removeClass(
                          document.querySelector(".login-dialog-wrap"),
                          "login-dialog-wrap--is-show"
                        );
                      loginSuccessCallBack(function () {
                        onLoginSuccess(_res);
                      });
                    }
                  } else if (options.guideType === 1) {
                    if (window.location.pathname === "/user/login") {
                      window.location.replace(
                        host.frontend +
                          "/guide?next=" +
                          getNextUrlParam("next") || ""
                      );
                    } else {
                      window.location.replace(
                        host.frontend +
                          "/guide?t=" +
                          (!isSxsWeb()
                            ? localStorage.getItem("sxsToken")
                            : "") +
                          "&next=" +
                          location.href
                      );
                    }
                  } else {
                    onLoginSuccess(_res);
                  }
                },
              });
            });
          } else if ($res.code === 322) {
            if (window.xMethod) {
              window.xMethod.sendData({
                event_type: "login",
                event_id: "web_1000019",
                ext_value: "验证码已失效，请重新获取",
              });
            }
            showAlert({
              type: "error",
              message: "验证码已失效，请重新获取",
            });
          } else {
            if (window.xMethod) {
              window.xMethod.sendData({
                event_type: "login",
                event_id: "web_1000019",
                ext_value: $res.msg,
              });
            }
            showAlert({
              type: "error",
              message: $res.msg,
            });
          }
        },
      });
    }

    function validateVerifyCode() {
      if (!_this.formData.rdcode) {
        showError("请输入验证码", "verifyCode");
        return false;
      } else {
        clearError("verifyCode");
        return true;
      }
    }

    function validatePhoneNumber(type) {
      var regexp = /^1[0-9]{10}$/;
      if (!_this.formData.tel) {
        if (type === "verify" && window.xMethod) {
          window.xMethod.sendData({
            event_type: "login",
            event_id: "web_1000013",
            ext_value: "请输入手机号",
          });
        }
        showError("请输入手机号", "phoneNumber");
        return false;
      } else if (
        _this.formData.areaCode == "+86" &&
        !regexp.test(_this.formData.tel)
      ) {
        if (type === "verify" && window.xMethod) {
          window.xMethod.sendData({
            event_type: "login",
            event_id: "web_1000013",
            ext_value: "请输入正确的手机号",
          });
        }
        showError("请输入正确的手机号", "phoneNumber");
        return false;
      } else {
        clearError("phoneNumber");
        return true;
      }
    }

    function clearError(field) {
      if (errMsgInline && field) {
        removeClass(_this.inputWrapEls[field], "input-wrap--is-error");
        _this.inputWrapEls[field].getElementsByClassName(
          "error-msg"
        )[0].innerText = "";
      }
    }

    function showError(msg, field) {
      msg = msg || "";
      if (errMsgInline && field) {
        addClass(_this.inputWrapEls[field], "input-wrap--is-error");
        _this.inputWrapEls[field].getElementsByClassName(
          "error-msg"
        )[0].innerText = msg;
      } else {
        showAlert({
          message: msg,
          type: "error",
        });
      }
    }

    function render(el) {
      _this.el = el;
      _this.el.innerHTML =
        '<div class="input-wrap input-wrap--phone-number">\
           <div class="input-wrap-icon">\
             <img class="wrap-icon" src="' +
        staticUrl +
        "login/popup/phone.png" +
        '" alt=""/>\
           </div>\
           <div class="area-code-wrap">\
             <div class="area-code">+86</div>\
             <div class="area-code-option"></div>\
           </div>\
           <input type="text" class="phone-number-input" placeholder="请输入手机号码" autocomplete="username" name="username">\
           <span class="error-msg"></span>\
         </div>\
         <div class="input-wrap input-wrap--verify-code">\
           <div class="input-wrap-icon">\
             <img class="wrap-icon" src="' +
        staticUrl +
        "login/popup/sms.png" +
        '" alt=""/>\
           </div>\
           <input type="text" class="verify-code-input" placeholder="请输入验证码" autocomplete="noope">\
           <div class="verify-code-wrap">\
             <span class="get-verify-code-btn">获取验证码</span>\
             <div class="verify-code-panel"></div>\
           </div>\
           <span class="error-msg"></span>\
         </div>\
         <button class="login-btn" type="button">登录/注册</button>';

      addClass(_this.el, "login-form login-form--phone");
    }
  }

  function AreaCodeOptionsPanel(options) {
    var _this = this;
    options = options || {};
    _this.el = options.el;
    EventBus.once(
      "area-code-options-loaded",
      function (options) {
        createElement({
          node: _this.el,
          children: options.map(function (group) {
            return {
              attrs: {
                class: "area-code-option__group",
              },
              children: [
                {
                  attrs: {
                    class: "area-code-option__title",
                  },
                  children: group.title,
                },
                {
                  attrs: {
                    class: "area-code-option__list",
                  },
                  children: group.options.map(function (item) {
                    return {
                      attrs: {
                        class: "area-code-option__item",
                      },
                      children: [
                        {
                          node: "span",
                          attrs: {
                            class: "area-code-option__label",
                          },
                          children: item.label,
                        },
                        {
                          node: "span",
                          attrs: {
                            class: "area-code-option__code",
                          },
                          children: item.code,
                        },
                      ],
                    };
                  }),
                },
              ],
            };
          }),
        });
      },
      true
    );

    var cancelClickOutsideAreaCodeoption = noop;

    _this.show = function () {
      if (isTv) {
        resetDom();
      }
      if (!hasClass(_this.el, "area-code-option--is-show")) {
        addClass(_this.el, "area-code-option--is-show");
        _this.trigger("show");

        cancelClickOutsideAreaCodeoption = listenClickOutside(
          _this.el,
          function () {
            _this.hide();
          }
        );
      }
    };

    _this.hide = function () {
      if (hasClass(_this.el, "area-code-option--is-show")) {
        removeClass(_this.el, "area-code-option--is-show");
        cancelClickOutsideAreaCodeoption();
        _this.trigger("hide");
      }
    };

    _this.eventBus = createEventBus();
    _this.on = _this.eventBus.on;
    _this.off = _this.eventBus.off;
    _this.once = _this.eventBus.once;
    _this.trigger = _this.eventBus.trigger;

    delegate(
      _this.el,
      "click",
      function (node) {
        return hasClass(node, "area-code-option__item");
      },
      function onAreaCodeOptionClick(e, target) {
        if (window.xMethod) {
          window.xMethod.sendData({
            event_type: "login",
            event_id: "web_1000012",
          });
        }
        var code = target.getElementsByClassName("area-code-option__code")[0]
          .innerText;
        var label = target.getElementsByClassName("area-code-option__label")[0]
          .innerText;
        _this.eventBus.trigger(
          "select",
          {
            label: label,
            code: code,
          },
          true
        );
        _this.hide();
      }
    );
  }

  // function fetchVerifyCode() {
  //   ajax('get', host.mainsite + '/validav2', {
  //     success: function(res) {
  //       if (res.code == 100) {
  //         EventBus.trigger('verify-code-loaded', res.msg, true)
  //       } else {
  //         showAlert({
  //           type: 'error',
  //           message: res.msg
  //         })
  //       }
  //     },
  //     fail: function(err) {
  //       console.error(err)
  //     }
  //   })
  // }

  function fetchAreaCode() {
    var h = host.mainsite;
    if (h.match(/dev/)) {
      h = h.replace("dev", "sit1");
    }
    ajax("get", h + "/app/phone/area", {
      success: function (res) {
        if (res.code == 100) {
          EventBus.trigger("area-code-options-loaded", res.msg, true);
        } else {
          showAlert({
            type: "error",
            message: res.msg,
          });
        }
      },
      fail: function (err) {
        console.error(err);
      },
    });
  }

  function createElement(domTree) {
    var node = domTree.node || "div";
    var attrs = domTree.attrs || {};
    var children = domTree.children || [];
    var fragment = document.createDocumentFragment();
    var el;

    if (node instanceof Element) {
      el = node;
    } else if (isString(node)) {
      el = document.createElement(node);
    } else {
      return;
    }

    Object.keys(attrs).forEach(function (attrKey) {
      var attrVal = attrs[attrKey];
      // 对style对象做特殊处理
      if (attrKey === "style" && isObject(attrVal)) {
        attrVal = Object.keys(attrVal).reduce(function (prevVal, styleKey) {
          return prevVal + styleKey + ":" + attrVal[styleKey] + ";";
        }, "");
      }
      el.setAttribute(attrKey, attrVal);
    });

    if (isString(children)) {
      el.innerText = children;
    } else if (isArray(children))
      for (var i = 0; i < children.length; i++) {
        var child = children[i];
        fragment.appendChild(createElement(child));
      }
    el.appendChild(fragment);

    return el;
  }

  function noop() {}

  function ajax(method, url, option) {
    var sxsToken = localStorage.getItem("sxsToken") || "";
    option = option || {};
    option.responseType = option.responseType || "json";
    var method = method || "get";
    var params = option.params || {};
    var url = (url || "") + qs(params);
    var success = isFunction(option.success) ? option.success : noop;
    var fail = isFunction(option.fail) ? option.fail : noop;
    var contentType = option.contentType || "urlencoded";
    var contentTypeMap = {
      json: "application/json;charset=UTF-8",
      urlencoded: "application/x-www-form-urlencoded; charset=UTF-8",
    };
    var response;
    var obj;
    if (url.match(/\/guide|\/baseinfo|\/detail/) && !isSxsWeb()) {
      obj = {
        token: sxsToken,
        "Content-type": contentTypeMap[contentType],
      };
    } else {
      obj = {
        "Content-type": contentTypeMap[contentType],
      };
    }
    var headers = copyFrom(obj, option.headers || {});
    var data = null;
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
      if (xhr.readyState == 4) {
        if (
          option.responseType === "json" &&
          typeof xhr.response === "string"
        ) {
          // IE 不支持 responseType json
          response = JSON.parse(xhr.response);
        } else {
          response = xhr.response;
        }
        if (xhr.status >= 200 && xhr.status < 300) {
          success(response);
        } else {
          fail(response);
        }
      }
    };

    xhr.open(method, url, true);

    xhr.withCredentials = true;

    Object.keys(headers).forEach(function (headerKey) {
      xhr.setRequestHeader(headerKey, headers[headerKey]);
    });

    if (option.data) {
      if (headers["Content-type"].indexOf("urlencoded") >= 0) {
        data = Object.keys(option.data)
          .map(function (key) {
            return (
              encodeURIComponent(key) +
              "=" +
              encodeURIComponent(option.data[key])
            );
          })
          .join("&");
      } else if (headers["Content-type"].indexOf("json") >= 0) {
        data = JSON.stringify(option.data);
      }
    }

    xhr.responseType = option.responseType;

    xhr.send(data);

    function qs(obj) {
      var str = "";
      if (isObject(obj)) {
        var keys = Object.keys(obj);
        if (keys.length > 0) {
          str =
            "?" +
            keys
              .map(function (key) {
                return (
                  encodeURIComponent(key) + "=" + encodeURIComponent(obj[key])
                );
              })
              .join("&");
        }
        return str;
      }
    }
  }

  function isArray(src) {
    return Object.prototype.toString.apply(src) === "[object Array]";
  }

  function isObject(src) {
    return typeof src === "object" && src !== null;
  }

  function isFunction(src) {
    return typeof src === "function";
  }

  function isString(src) {
    return typeof src === "string";
  }

  function copyFrom(dest, src, deep) {
    if (!dest) {
      dest = isArray(src) ? [] : {};
    }
    if (!src) {
      return dest;
    }
    for (var i in src) {
      if (deep && isObject(src[i])) {
        dest[i] = isArray(src[i]) ? [] : {};
        copyFrom(dest[i], src[i], deep);
      } else {
        dest[i] = src[i];
      }
    }
    return dest;
  }

  function myencode(source) {
    var nstr = [],
      key = [23, 24, 39, 38, 22, 11, 13, 63],
      s,
      str = source.slice(0).split("");

    while (str.length) {
      s = str.shift();
      nstr.push(String(s.charCodeAt()).split("").reverse().join(""));
    }
    nstr = nstr.reverse().join("X");

    return nstr;
  }

  function defaultTransformFormData(formData) {
    return formData;
  }

  /**
   * 监听点击元素外部的事件
   * @param {Element} node 要监听的元素
   * @param {function} handler 回调函数
   * @returns {fucntion} 取消监听的函数
   */
  function listenClickOutside(node, handler) {
    /**
     * 可能是点击外部调用的这个函数，如果直接加上点击事件
     * click事件马上会触发，然后就关闭了
     * 为了避免这种情况，在下一个事件循环再加上点击事件
     */
    setTimeout(function () {
      document.addEventListener("click", onClick);
    });

    function onClick(e) {
      var isChildOfNode = false;
      var currentNode = e.target;
      // 判断是不是点击了 node 的子元素或本身
      while (currentNode) {
        if (currentNode === node) {
          isChildOfNode = true;
          break;
        } else {
          currentNode = currentNode.parentNode;
        }
      }
      if (!isChildOfNode) {
        handler();
      }
    }

    // 返回取消监听函数
    return function cancelClickOutside() {
      document.removeEventListener("click", onClick);
    };
  }

  function delegate(node, evnetName, selector, fn) {
    node.addEventListener(evnetName, function (e) {
      var currentNode = e.target;

      while (currentNode && currentNode !== node) {
        if (selector(currentNode)) {
          fn(e, currentNode);
          break;
        } else {
          currentNode = currentNode.parentNode;
        }
      }
    });
  }

  function addClass(node, className) {
    var nodeClassList = node.className.split(" ");
    var classNameList = className.split(" ");
    classNameList.forEach(function (className) {
      if (nodeClassList.indexOf(className) === -1) {
        nodeClassList.push(className);
      }
    });
    node.className = nodeClassList.join(" ");
  }

  function hasClass(node, className) {
    var nodeClassList = node.className.split(" ");
    return nodeClassList.indexOf(className) >= 0;
  }

  function removeClass(node, className) {
    var nodeClassList = node.className.split(" ");
    var classNameList = className.split(" ");
    node.className = nodeClassList
      .filter(function (nodeClass) {
        var index = classNameList.indexOf(nodeClass);
        if (index >= 0) {
          classNameList.splice(index, 1);
          return false;
        }
        return true;
      })
      .join(" ");
  }

  function replaceNode(newNode, oldNode) {
    oldNode.parentNode.replaceChild(newNode, oldNode);
  }

  function findInArr(arr, fn) {
    var index = findIndexInArr(arr, fn);
    if (index >= 0) {
      return arr[index];
    } else {
      return null;
    }
  }

  function findIndexInArr(arr, fn) {
    for (var i = 0; i < arr.length; i++) {
      if (fn(arr[i])) {
        return i;
      }
    }
    return -1;
  }

  function createEventBus() {
    var cachedData = {};
    var eventCbs = {};

    function on(eventName, fn, useCachedData) {
      eventCbs[eventName] = eventCbs[eventName] || [];
      if (useCachedData && cachedData[eventName]) {
        fn(cachedData[eventName]);
      }
      if (!_hasCb(eventName, fn)) {
        eventCbs[eventName].push({
          cb: fn,
          isOnce: false,
        });
      }
    }

    function once(eventName, fn, useCachedData) {
      eventCbs[eventName] = eventCbs[eventName] || [];
      if (useCachedData && cachedData[eventName]) {
        fn(cachedData[eventName]);
      } else {
        if (!_hasCb(eventName, fn)) {
          eventCbs[eventName].push({
            cb: fn,
            isOnce: true,
          });
        }
      }
    }

    function off(eventName, fn) {
      if (!fn) {
        eventCbs[eventName] = [];
      } else if (eventCbs[eventName]) {
        eventCbs[eventName] = eventCbs[eventName].filter(function (fn) {
          return eventCbs[eventName][i].cb !== fn;
        });
      }
    }

    function trigger(eventName, val, shouldCacheData) {
      if (shouldCacheData) {
        cachedData[eventName] = val;
      }
      if (isArray(eventCbs[eventName])) {
        eventCbs[eventName] = eventCbs[eventName].filter(function (fn) {
          if (isFunction(fn.cb)) {
            fn.cb(val);
          }
          return !fn.isOnce;
        });
      }
    }

    function _hasCb(eventName, cb) {
      var index = findIndexInArr(eventCbs[eventName], function (item) {
        return item.cb === cb;
      });
      return index >= 0;
    }

    return {
      on: on,
      once: once,
      off: off,
      trigger: trigger,
    };
  }

  function defaultLoginSuccessHandler(res) {
    if (window.xMethod) {
      window.xMethod.sendData({
        event_type: "login",
        event_id: "web_1000020",
        ext_value: "弹窗",
      });
    }
    if (res.msg === "company") {
      window.location.href = "http://hr.shixiseng.com";
    } else {
      window.location.reload();
    }
  }

  function showAlert(option) {
    var message = (option && option.message) || "";
    var type = (option && option.type) || "info";
    var duration = (option && option.duration) || 3000;
    var el = document.createElement("div");
    el.className = "alert" + (type ? " alert--" + type : "");
    el.innerText = message;
    document.body.appendChild(el);
    el.offsetWidth; // 强制重绘

    addClass(el, "alert--active");

    setTimeout(function () {
      removeClass(el, "alert--active");
      setTimeout(function () {
        document.body.removeChild(el);
      }, 1000);
    }, duration);
  }

  function getHost() {
    var hostPrefix = location.host.split(".")[0];
    switch (hostPrefix) {
      case "localhost:8700":
        return {
          mainsite: "http://sit1-sxs-web.mshare.cn",
          frontend: "http://sit1-sxs-frontend.mshare.cn",
          newApiHost: "http://istio-test-apigateway.mshare.cn",
          optionHost: "http://sit1-ad-service.mshare.cn",
          //hr: 'https://hr.shixiseng.com/#/signon',
          liveApi: "http://dev-live-api-server.mshare.cn",
          hrHost: "http://dev-hr-frontend-v2.mshare.cn",
        };
      case "sit1-local":
        return {
          mainsite: "http://dev-sxs-web.mshare.cn",
          frontend: "http://dev-sxs-frontend.mshare.cn",
          newApiHost: "http://istio-test-apigateway.mshare.cn",
          optionHost: "http://dev-ad-service.mshare.cn",
          liveApi: "http://sit1-live-api-server.mshare.cn",
          hrHost: "http://sit1-hr-frontend-v2.mshare.cn",
        };
      case "www":
      case "tv":
      case "resume":
      case "tuiguang":
      case "edu":
      case "qianbei":
      case "ac":
      case "live":
      case "acca":
      case "case":
      case "haoqi":
      case "career":
      case "xiaoyuan":
      case "act":
      case "baike":
      case "search":
      case "exam":
      case "ee-career":
      case "ieltsjob":
        return {
          mainsite: "https://www.shixiseng.com",
          frontend: "https://resume.shixiseng.com",
          newApiHost: "https://apigateway.shixiseng.com",
          optionHost: "https://operation.shixiseng.com",
          liveApi: "https://live-api.shixiseng.com",
          hrHost: "https://hr.shixiseng.com",
        };
      case "wwwnew":
      case "resumenew":
        return {
          mainsite: "https://wwwnew.shixiseng.com",
          frontend: "https://resumenew.shixiseng.com",
          newApiHost: "https://apigateway.shixiseng.com",
          optionHost: "https://operation.shixiseng.com",
        };
      default:
        var env =
          hostPrefix.split("-")[0] > 1 ? "sit1" : hostPrefix.split("-")[0];
        var istioEnv;
        if (env !== "dev" && env !== "uat") {
          istioEnv = "test";
        } else {
          istioEnv = env;
        }
        if (hostPrefix.indexOf("localhost") >= 0) {
          return {
            mainsite: "http://sit1-sxs-web.mshare.cn",
            frontend: "http://sit1-sxs-frontend.mshare.cn",
            newApiHost: "http://istio-test-apigateway.mshare.cn",
            optionHost: "http://sit1-ad-service.mshare.cn",
          };
        } else {
          return {
            mainsite:
              location.protocol == "https"
                ? "//" + env + "-sxs-api.mshare.cn"
                : "//" + env + "-sxs-web.mshare.cn",
            frontend: "http://" + env + "-sxs-frontend.mshare.cn",
            newApiHost: "//istio-" + istioEnv + "-apigateway.mshare.cn",
            optionHost: "http://" + env + "-ad-service.mshare.cn",
            liveApi:
              env == "uat"
                ? "http://uat-live-api.mshare.cn"
                : "http://" + env + "-live-api-server.mshare.cn",
            hrHost: "http://" + env + "-hr-frontend-v2.mshare.cn",
          };
        }
    }
  }

  return {
    ajax: ajax,
    PhoneLoginForm: PhoneLoginForm,
    PwdLoginForm: PwdLoginForm,
    LoginPanel: LoginPanel,
    EventBus: EventBus,
    showAlert: showAlert,
    LoginDialog: LoginDialog,
    FooterLogin: FooterLogin,
  };
});
