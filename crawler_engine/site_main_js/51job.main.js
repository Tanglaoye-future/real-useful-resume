!function() {
    "use strict";
    var e = {};
    window.__51global = e,
    function(e) {
        window.onerror = function(e, t, n, o, a) {}
        ,
        window.addEventListener && window.addEventListener("unhandledrejection", function(e) {
            e.preventDefault();
        });
        var t = Object.defineProperty || !1;
        if (t)
            try {
                t({}, "a", {
                    value: 1
                });
            } catch (e) {
                t = !1;
            }
        var n = "undefined" != typeof Proxy
          , o = !(void 0 === window.console || "undefined" == typeof console)
          , a = n;
        var r = !1 === document.createElement("script").noModule;
        function i(e) {
            return "[object String]" === Object.prototype.toString.call(e);
        }
        e.isSupportES6Proxy = n,
        e.isSupportVue3 = a,
        o || (window.console = {
            log: function log(e) {},
            info: function info(e) {},
            warn: function warn(e) {},
            error: function error(e) {},
            debug: function debug(e) {}
        });
        var d = !!document.querySelector;
        function c(e) {
            return "#" === (e = e.replace(/^\s+|\s+$/g, "")).charAt(0) ? l(e)[0] || null : l(e);
        }
        function l(e) {
            var t = document
              , n = (e = e.replace(/^\s+|\s+$/g, "")).charAt(0)
              , o = [];
            if (d)
                return t.querySelectorAll(e);
            if ("#" === n) {
                var a = e.slice(1);
                return o.push(document.getElementById(a)),
                o;
            }
            if ("." === n && t.getElementsByClassName) {
                var r = e.slice(1);
                return o = t.getElementsByClassName(r);
            }
            var i = e.match(/^(\w+)/);
            if (i)
                for (var c = i[1], l = (o = t.getElementsByTagName(c),
                0); l < o.length; l++) {
                    var s = o[l]
                      , u = e.match(/\[([^\]]+)\]/);
                    if (u) {
                        var f = u[1].match(/([a-z0-9_-]+)(?:=(["'])?([^"']*)\2)?/i);
                        if (f) {
                            var v = f[1]
                              , E = f[3];
                            if (s.getAttribute(v) !== E)
                                continue;
                        }
                    }
                    e.indexOf("#") > -1 && s.id !== e.split("#")[1] || e.indexOf(".") > -1 && s.className !== e.split(".")[1] || o.push(s);
                }
            return o;
        }
        var s = !1;
        s = !1,
        e.querySelector = c,
        e.querySelectorAll = l,
        e.onReady = function(t) {
            if (s)
                n();
            else {
                var n = function n() {
                    if (!s) {
                        s = !0;
                        try {
                            t(e),
                            function() {
                                if ((n = window.navigator.userAgent).indexOf("MSIE ") > -1 || n.indexOf("Trident/") > -1) {
                                    var e = c("#headerWarning")
                                      , t = c("#loginWarning");
                                    e && (e.style.display = "block"),
                                    t && (t.style.display = "block");
                                }
                                var n;
                            }();
                        } catch (e) {}
                    }
                };
                document.addEventListener ? (document.addEventListener("DOMContentLoaded", function e() {
                    document.removeEventListener("DOMContentLoaded", e, !1),
                    window.removeEventListener("load", e, !1),
                    n();
                }, !1),
                window.addEventListener("load", function e() {
                    window.removeEventListener("load", e, !1),
                    n();
                }, !1)) : document.attachEvent ? (document.attachEvent("onreadystatechange", function e() {
                    "complete" === document.readyState && (document.detachEvent("onreadystatechange", e),
                    n());
                }),
                window == top && window.attachEvent("onload", function e() {
                    window.detachEvent("onload", e),
                    n();
                })) : n();
            }
        }
        ,
        e.loadScript = function(e, t, n) {
            var o = !1 !== (n = n || {}).async
              , a = n.id || ""
              , r = document.createElement("script");
            function i() {
                r.onload = null,
                r.onerror = null,
                r.onreadystatechange = null,
                r.onabort = null;
            }
            r.type = "text/javascript",
            r.src = e,
            r.async = o,
            a && (r.id = a),
            "onload"in r ? (r.onload = function() {
                i(),
                t && t();
            }
            ,
            r.onerror = function() {
                i(),
                t && t(new Error("Failed to load script: " + e));
            }
            ) : r.onreadystatechange = function() {
                "loaded" !== r.readyState && "complete" !== r.readyState || (i(),
                t && t());
            }
            ,
            r.onabort = function() {
                i(),
                t && t(new Error("Script loading aborted: " + e));
            }
            ,
            document.getElementsByTagName("head")[0].appendChild(r);
        }
        ,
        e.removeEventListener = function e(t, n, o, a) {
            var r;
            if (o)
                if (i(t))
                    e(c(t), n, o, a);
                else if (r = t,
                "[object Array]" !== Object.prototype.toString.call(r)) {
                    if (a = a || !1,
                    t.removeEventListener)
                        t.removeEventListener(n, o, a);
                    else if (t.detachEvent && o._attachedEvents) {
                        var d = "on" + n
                          , l = o._attachedEvents[d];
                        l && (t.detachEvent(d, l),
                        delete o._attachedEvents[d]);
                    } else {
                        "function" == typeof t[d = "on" + n] && (t[d] = null);
                    }
                } else
                    for (var s = 0; s < t.length; s++)
                        e(t[s], n, o, a);
        }
        ,
        e.addEventListener = function e(t, n, o, a) {
            if (o && t)
                if (i(t))
                    e(c(t), n, o, a);
                else if (t)
                    if (t.length)
                        for (var r = 0; r < t.length; r++)
                            e(t[r], n, o, a);
                    else if (a = a || !1,
                    t.addEventListener)
                        t.addEventListener(n, o, a);
                    else if (t.attachEvent) {
                        var d = function d() {
                            o.apply(t, arguments);
                        };
                        o._attachedEvents || (o._attachedEvents = {});
                        var l = "on" + n;
                        o._attachedEvents[l] = d,
                        t.attachEvent(l, d);
                    } else {
                        if ("function" == typeof t[l = "on" + n]) {
                            var s = t[l];
                            t[l] = function() {
                                s(),
                                o();
                            }
                            ;
                        } else
                            t[l] = o;
                    }
        }
        ,
        e.isSupportsModule = r,
        e.isModernBrowser = !1,
        e.$defineProperty = t;
    }(e);
}();
