!function() {
    "use strict";
    var n, t = function() {
        return (t = Object.assign || function(n) {
            for (var t, e = 1, r = arguments.length; e < r; e++)
                for (var o in t = arguments[e])
                    Object.prototype.hasOwnProperty.call(t, o) && (n[o] = t[o]);
            return n
        }
        ).apply(this, arguments)
    };
    function e(n, t) {
        var e = "function" == typeof Symbol && n[Symbol.iterator];
        if (!e)
            return n;
        var r, o, i = e.call(n), u = [];
        try {
            for (; (void 0 === t || 0 < t--) && !(r = i.next()).done; )
                u.push(r.value)
        } catch (n) {
            o = {
                error: n
            }
        } finally {
            try {
                r && !r.done && (e = i.return) && e.call(i)
            } finally {
                if (o)
                    throw o.error
            }
        }
        return u
    }
    function r(n, t, e) {
        if (e || 2 == arguments.length)
            for (var r, o = 0, i = t.length; o < i; o++)
                !r && o in t || ((r = r || Array.prototype.slice.call(t, 0, o))[o] = t[o]);
        return n.concat(r || Array.prototype.slice.call(t))
    }
    function o(n) {
        return JSON.stringify({
            ev_type: "batch",
            list: n
        })
    }
    "undefined" == typeof Element || Element.prototype.addEventListener || (n = [],
    rt = function(t, e) {
        for (var r = 0; r < n.length; ) {
            var o = n[r];
            if (o.object === this && o.type === t && o.listener === e) {
                "DOMContentLoaded" === t ? this.detachEvent("onreadystatechange", o.wrapper) : this.detachEvent("on" + t, o.wrapper),
                n.splice(r, 1);
                break
            }
            ++r
        }
    }
    ,
    Element.prototype.addEventListener = rn = function(t, e) {
        function r(n) {
            n.target = n.srcElement,
            n.currentTarget = u,
            void 0 !== e.handleEvent ? e.handleEvent(n) : e.call(u, n)
        }
        var o, i, u = this;
        "DOMContentLoaded" === t ? (o = function(n) {
            "complete" === document.readyState && r(n)
        }
        ,
        document.attachEvent("onreadystatechange", o),
        n.push({
            object: this,
            type: t,
            listener: e,
            wrapper: o
        }),
        "complete" === document.readyState && ((i = new window.Event).srcElement = window,
        o(i))) : (this.attachEvent("on" + t, r),
        n.push({
            object: this,
            type: t,
            listener: e,
            wrapper: r
        }))
    }
    ,
    Element.prototype.removeEventListener = rt,
    HTMLDocument && !HTMLDocument.prototype.addEventListener && (HTMLDocument.prototype.addEventListener = rn,
    HTMLDocument.prototype.removeEventListener = rt),
    Window && !Window.prototype.addEventListener && (Window.prototype.addEventListener = rn,
    Window.prototype.removeEventListener = rt));
    var i = ["init", "start", "config", "beforeDestroy", "provide", "beforeReport", "report", "beforeBuild", "build", "beforeSend", "send", "beforeConfig"]
      , u = function() {
        return {}
    };
    function a(n) {
        return n
    }
    function c(n) {
        return "object" == typeof n && null !== n
    }
    var f = Object.prototype;
    function s(n) {
        if (c(n))
            return "function" != typeof Object.getPrototypeOf ? "[object Object]" === f.toString.call(n) : (n = Object.getPrototypeOf(n)) === f || null === n
    }
    function l(n) {
        return "[object Array]" === f.toString.call(n)
    }
    function d(n) {
        return "function" == typeof n
    }
    function p(n) {
        return "number" == typeof n
    }
    function v(n) {
        return "string" == typeof n
    }
    function h(n, t) {
        if (!l(n) || 0 === n.length)
            return !1;
        for (var e = 0; e < n.length; ) {
            if (n[e] === t)
                return !0;
            e++
        }
        return !1
    }
    function m(n, t) {
        if (!l(n))
            return n;
        var e = n.indexOf(t);
        return 0 <= e ? ((t = n.slice()).splice(e, 1),
        t) : n
    }
    function g(n, t, r) {
        for (var o, i = (t = e(t.split(".")))[0], u = t.slice(1); n && 0 < u.length; )
            n = n[i],
            i = (o = e(u))[0],
            u = o.slice(1);
        if (n)
            return r(n, i)
    }
    function y(n) {
        return l(n) && n.length ? function(n) {
            for (var t = [], e = n.length, r = 0; r < e; r++) {
                var o = n[r];
                v(o) ? t.push(o.replace(/([.*+?^=!:${}()|[\]/\\])/g, "\\$1")) : o && o.source && t.push(o.source)
            }
            return RegExp(t.join("|"), "i")
        }(n) : null
    }
    var b = function(n, t) {
        return !!(n = y(n || [])) && n.test(t)
    };
    function _(n) {
        try {
            return v(n) ? n : JSON.stringify(n)
        } catch (n) {
            return "[FAILED_TO_STRINGIFY]:" + String(n)
        }
    }
    function w(n, t, o, i) {
        return void 0 === i && (i = !0),
        function() {
            for (var a = [], c = 0; c < arguments.length; c++)
                a[c] = arguments[c];
            if (!n)
                return u;
            var f = n[t]
              , s = o.apply(void 0, r([f], e(a), !1))
              , l = s;
            return d(l) && i && (l = function() {
                for (var n = [], t = 0; t < arguments.length; t++)
                    n[t] = arguments[t];
                try {
                    return s.apply(this, n)
                } catch (t) {
                    return d(f) && f.apply(this, n)
                }
            }
            ),
            n[t] = l,
            function(e) {
                e || (l === n[t] ? n[t] = f : s = f)
            }
        }
    }
    function x() {
        for (var n = [], t = 0; t < arguments.length; t++)
            n[t] = arguments[t];
        console.warn.apply(console, r(["[SDK]", Date.now(), T("" + k++)], e(n), !1))
    }
    function E(n) {
        return function(t) {
            for (var e = t, r = 0; r < n.length && e; r++)
                try {
                    e = n[r](e)
                } catch (n) {
                    j(n)
                }
            return e
        }
    }
    var S = function(n, t, o) {
        return function() {
            for (var i = [], a = 0; a < arguments.length; a++)
                i[a] = arguments[a];
            if (!n)
                return u;
            var c = n[t]
              , f = o.apply(void 0, r([c], e(i), !1))
              , s = f;
            return d(s) && (s = function() {
                for (var n = [], t = 0; t < arguments.length; t++)
                    n[t] = arguments[t];
                return f.apply(this, n)
            }
            ),
            n[t] = s,
            function() {
                s === n[t] ? n[t] = c : f = c
            }
        }
    }
      , T = "".padStart ? function(n, t) {
        return n.padStart(t = void 0 === t ? 8 : t, " ")
    }
    : function(n) {
        return n
    }
      , R = 0
      , j = function() {
        for (var n = [], t = 0; t < arguments.length; t++)
            n[t] = arguments[t];
        console.error.apply(console, r(["[SDK]", Date.now(), T("" + R++)], e(n), !1))
    }
      , k = 0
      , C = function(n) {
        return Math.random() < Number(n)
    }
      , O = function(n, t) {
        return n < Number(t)
    };
    function L() {
        var n = function() {
            for (var n = Array(16), t = 0, e = 0; e < 16; e++)
                0 == (3 & e) && (t = 0x100000000 * Math.random()),
                n[e] = t >>> ((3 & e) << 3) & 255;
            return n
        }();
        return n[6] = 15 & n[6] | 64,
        n[8] = 63 & n[8] | 128,
        function(n) {
            for (var t = [], e = 0; e < 256; ++e)
                t[e] = (e + 256).toString(16).substr(1);
            var r = 0;
            return [t[n[r++]], t[n[r++]], t[n[r++]], t[n[r++]], "-", t[n[r++]], t[n[r++]], "-", t[n[r++]], t[n[r++]], "-", t[n[r++]], t[n[r++]], "-", t[n[r++]], t[n[r++]], t[n[r++]], t[n[r++]], t[n[+r]], t[n[15]]].join("")
        }(n)
    }
    var M = function(n) {
        function t(n) {
            a = m(a, n),
            f || s()
        }
        var e, r, o, i, a = [], c = [], f = !1, s = (r = function() {
            f = !0,
            e && e[0](),
            c.forEach(function(n) {
                return n()
            }),
            c.length = 0,
            e = void 0
        }
        ,
        -1 === (o = n = void (i = 0) === n ? 3e5 : n) ? u : function() {
            if (a.length)
                return i && clearTimeout(i),
                void (i = 0);
            0 === i && (i = setTimeout(r, o))
        }
        );
        return {
            next: function(n) {
                return function n(t, e) {
                    var r = [];
                    try {
                        r = e.reduce(function(n, e) {
                            try {
                                var r = e(t);
                                "function" == typeof r && n.push(r)
                            } catch (n) {}
                            return n
                        }, [])
                    } catch (n) {}
                    return function(t) {
                        return n(t, r)
                    }
                }(n, a)
            },
            complete: function(n) {
                c.push(n)
            },
            attach: function(n, t) {
                e = [n, t]
            },
            subscribe: function(n) {
                if (f)
                    throw Error("Observer is closed");
                return a.push(n),
                e && e[1] && e[1](n),
                s(),
                function() {
                    return t(n)
                }
            },
            unsubscribe: t
        }
    }
      , I = function(n, t, e) {
        e = M(e);
        try {
            n(e.next, e.attach),
            t && e.complete(t)
        } catch (n) {}
        return [e.subscribe, e.unsubscribe]
    }
      , q = function(n, t, e, r) {
        return n.destroyAgent.set(t, e, r)
    }
      , A = function(n) {
        var e, r, o, i = (e = {},
        r = {},
        o = {
            set: function(n, t) {
                return e[n] = t,
                r[n] = _(t),
                o
            },
            merge: function(n) {
                return e = t(t({}, e), n),
                Object.keys(n).forEach(function(t) {
                    r[t] = _(n[t])
                }),
                o
            },
            delete: function(n) {
                return delete e[n],
                delete r[n],
                o
            },
            clear: function() {
                return e = {},
                r = {},
                o
            },
            get: function(n) {
                return r[n]
            },
            toString: function() {
                return t({}, r)
            }
        });
        n.provide("context", i),
        n.on("report", function(n) {
            return n.extra || (n.extra = {}),
            n.extra.context = i.toString(),
            n
        })
    }
      , D = function(n, t, o) {
        function i() {
            for (var o = [], u = 0; u < arguments.length; u++)
                o[u] = arguments[u];
            var c = o[0];
            if (c) {
                var f = c.split(".")[0];
                if (f in i)
                    return l = i,
                    p = c,
                    s = [].slice.call(o, 1),
                    g(l, p, function(n, t) {
                        if (n && t in n && d(n[t]))
                            try {
                                return n[t].apply(n, s)
                            } catch (n) {
                                return
                            }
                    });
                var s, l = a[f] || [], p = null !== (p = null == t ? void 0 : t(n)) && void 0 !== p ? p : {};
                l.push(r([p], e(o), !1)),
                a[f] = l
            }
        }
        var u, a = {};
        for (u in w(n, "provide", function(t) {
            return function(e, r) {
                i[e] = r,
                t.call(n, e, r)
            }
        })(),
        n)
            Object.prototype.hasOwnProperty.call(n, u) && (i[u] = n[u]);
        return n.on("provide", function(t) {
            a[t] && (a[t].forEach(function(t) {
                var r = e(t)
                  , t = r[0]
                  , r = r.slice(1);
                null != o && o(n, t, r)
            }),
            a[t] = null)
        }),
        i
    };
    function N(n, t) {
        return n.initSubject(t)
    }
    function P(n, t, r) {
        var t = e(t, 2)
          , o = t[0]
          , t = t[1]
          , i = n.privateSubject || {};
        return i[o] || (i[o] = I(t, function() {
            i[o] = void 0
        }, r)),
        i[o]
    }
    var B = function() {
        return Date.now()
    };
    function H() {
        if ("object" == typeof window && c(window))
            return window
    }
    function U() {
        if ("object" == typeof document && c(document))
            return document
    }
    function W() {
        return H() && window.location
    }
    function F() {
        if (H() && c(window.performance))
            return window.performance
    }
    function X() {
        if ("function" == typeof XMLHttpRequest && d(XMLHttpRequest))
            return XMLHttpRequest
    }
    function z() {
        if (H() && d(window.MutationObserver))
            return window.MutationObserver
    }
    function G() {
        if (H() && d(window.PerformanceObserver))
            return window.PerformanceObserver
    }
    function J(n) {
        var t = U();
        return t && n ? ((t = t.createElement("a")).href = n,
        t.href) : ""
    }
    function Y(n) {
        var t = U();
        return t && n ? ((t = t.createElement("a")).href = n,
        "/" !== (n = t.pathname || "/")[0] && (n = "/" + n),
        {
            url: t.href,
            protocol: t.protocol.slice(0, -1),
            domain: t.hostname,
            query: t.search.substring(1),
            path: n,
            hash: t.hash
        }) : {
            url: n,
            protocol: "",
            domain: "",
            query: "",
            path: "",
            hash: ""
        }
    }
    function $() {
        var n = H() && W();
        return n ? n.href : ""
    }
    function V() {
        for (var n = [], t = 0; t < arguments.length; t++)
            n[t] = arguments[t];
        var e = ni(H());
        e && (e.errors || (e.errors = []),
        e.errors.push(n))
    }
    function K(n, t) {
        var e = n && new n(t);
        return [function(n, t) {
            e && n && e.observe(n, t)
        }
        , function() {
            return e && e.disconnect()
        }
        ]
    }
    var Q = function(n) {
        return {
            pid: n.pid,
            view_id: n.viewId,
            url: $()
        }
    }
      , Z = function(n) {
        var t = n.config()
          , t = Q(t);
        return t.context = n.context ? n.context.toString() : {},
        t
    }
      , nn = function(n, e) {
        void 0 === e && (e = !1);
        var r = Z(n);
        return e && (r.timestamp = B()),
        function(e) {
            n.report(t(t({}, e), {
                overrides: r
            }))
        }
    }
      , nt = "view_0"
      , ne = function(n) {
        return function(e, r) {
            function o(r) {
                var o;
                r.viewId && r.viewId !== (null === (o = n.config()) || void 0 === o ? void 0 : o.viewId) && (e(i),
                i = t(t({}, Z(n)), Q(r)))
            }
            var i = Z(n);
            n.on("beforeConfig", o),
            r(function() {
                n.off("beforeConfig", o)
            })
        }
    }
      , nr = "f_view_0"
      , no = function(n) {
        return function(t, e) {
            var r = Z(n);
            e(u, function(n) {
                r && n(r)
            })
        }
    }
      , ni = function(n) {
        if (n)
            return n.__SLARDAR_REGISTRY__ || (n.__SLARDAR_REGISTRY__ = {
                Slardar: {
                    plugins: [],
                    errors: [],
                    subject: {}
                }
            }),
            n.__SLARDAR_REGISTRY__.Slardar
    }
      , nu = function(n) {
        var t = n && n.timing || void 0;
        return [t, function() {
            return n && n.now ? n.now() : (Date.now ? Date.now() : +new Date) - (t && t.navigationStart || 0)
        }
        , function(t) {
            var e = (n || {}).getEntriesByType;
            return d(e) && e.call(n, t) || []
        }
        , function() {
            var t = (n || {}).clearResourceTimings;
            d(t) && t.call(n)
        }
        , function(t) {
            var e = (n || {}).getEntriesByName;
            return d(e) && e.call(n, t) || []
        }
        ]
    }
      , na = function(n) {
        var t = {
            url: $(),
            timestamp: B()
        }
          , e = n.config();
        return null != e && e.pid && (t.pid = e.pid),
        null != n && n.context && (t.context = n.context.toString()),
        t
    }
      , nc = function(n, t) {
        return function(e) {
            function r(n) {
                return n.overrides = t,
                n
            }
            n.on("report", r),
            e(),
            n.off("report", r)
        }
    }
      , nf = "<unknown>";
    function ns(n) {
        try {
            for (var t, e = n, r = [], o = 0, i = 0; e && o++ < 5 && !("html" === (t = function(n) {
                var t, e, r, o, i, u = n, a = [];
                if (!u || !u.tagName)
                    return "";
                if (a.push(u.tagName.toLowerCase()),
                u.id)
                    return "#" + u.id;
                if ((n = u.className) && v(n))
                    for (e = n.split(/\s+/),
                    i = 0; i < e.length; i++)
                        a.push("." + e[i]);
                var c = ["type", "name", "title", "alt"];
                for (i = 0; i < c.length; i++)
                    r = c[i],
                    (o = u.getAttribute(r)) && a.push("[" + r + '="' + o + '"]');
                for (var f = u, s = 1, l = !0; f = f.previousElementSibling; )
                    (null === (t = f.tagName) || void 0 === t ? void 0 : t.toLowerCase()) === (null === (t = u.tagName) || void 0 === t ? void 0 : t.toLowerCase()) && (f.className === u.className && c.every(function(n) {
                        return u.getAttribute(n) === (null == f ? void 0 : f.getAttribute(n))
                    }) && (l = !1),
                    s++);
                return 1 < s && !l && a.push(":nth-of-type(" + s + ")"),
                a.join("")
            }(e)) || 1 < o && 256 <= i + 3 * r.length + t.length); )
                r.push(t),
                i += t.length,
                e = e.parentNode;
            return r.reverse().join(" > ")
        } catch (n) {
            return nf
        }
    }
    var nl = function(n, t, e, r) {
        return void 0 === r && (r = !1),
        n.addEventListener(t, e, r),
        function() {
            n.removeEventListener(t, e, r)
        }
    }
      , nd = function(n, t, e, r) {
        return void 0 === r && (r = !1),
        n.addEventListener(t, e, r),
        function() {
            n.removeEventListener(t, e, r)
        }
    };
    function np() {
        return !!btoa && !!atob
    }
    var nv = function(n) {
        var t = !1;
        return [function(e) {
            t || (t = !0,
            n && n(e))
        }
        ]
    }
      , nh = function(n, e) {
        return c(n) ? t(t({}, e), n) : !!n && e
    };
    function nm(n, e, r) {
        var o;
        if (!(r <= 0))
            try {
                localStorage.setItem(n, (o = JSON.stringify(t(t({}, e), {
                    expires: B() + r
                })),
                np() ? btoa(encodeURI(o)) : o))
            } catch (n) {}
    }
    function ng(n) {
        return !1 === n ? 0 : !0 !== n && void 0 !== n && p(n) ? n : 7776e6
    }
    function ny() {
        var n = RegExp("\\/monitor_web\\/collect|\\/monitor_browser\\/collect\\/batch", "i");
        return function(t) {
            return n.test(t)
        }
    }
    function nb(n, t) {
        return function(e, r) {
            var o = t([e, r = void 0 === r ? {} : r])
              , r = n(e, r);
            return r.then(function(n) {
                o(n)
            }, function() {
                o(void 0)
            }),
            r
        }
    }
    function n_(n, t) {
        var e = nh(n, nJ);
        if (e && C(e.sampleRate))
            return function(n, r) {
                var o = e.origins;
                o.length && b(o, n) && (r("x-rum-traceparent", "00-" + nY() + "-" + nY().substring(16) + "-" + nG),
                r("x-rum-tracestate", t))
            }
    }
    function nw(n, t) {
        return !n || !t || n$.test(n) || nV.test(t)
    }
    var nx = "xhr_0"
      , nE = function(n) {
        return function() {
            for (var t, r = [], o = 0; o < arguments.length; o++)
                r[o] = arguments[o];
            return t = e(r, 2),
            this._method = t[0],
            this._url = t[1],
            n.apply(this, r)
        }
    }
      , nS = function(n) {
        return function() {
            for (var t = [], r = 0; r < arguments.length; r++)
                t[r] = arguments[r];
            this._reqHeaders = this._reqHeaders || {};
            var o = e(t, 2)
              , i = o[0]
              , o = o[1];
            return this._reqHeaders[i] = o,
            n && n.apply(this, t)
        }
    }
      , nT = function(n, t) {
        var e = ny();
        return function() {
            for (var r, o, i = [], u = 0; u < arguments.length; u++)
                i[u] = arguments[u];
            return this._start = B(),
            this._data = null == i ? void 0 : i[0],
            e(this._url) || (r = t([this._method, this._url, this._start, this]),
            S(o = this, "onreadystatechange", function(n) {
                return function() {
                    for (var t = [], e = 0; e < arguments.length; e++)
                        t[e] = arguments[e];
                    return 4 === this.readyState && r(o),
                    n && n.apply(this, t)
                }
            })()),
            n.apply(this, i)
        }
    }
      , nR = function(n) {
        return function(t, e) {
            var r;
            n && ((r = []).push(S(n, "open", nE)()),
            r.push(S(n, "setRequestHeader", nS)()),
            r.push(S(n, "send", nT)(t)),
            e(function() {
                r.forEach(function(n) {
                    return n()
                })
            }))
        }
    }
      , nj = ["fetch_0", function(n, t) {
        var e, r = H();
        r && fetch && ((e = []).push(S(r, "fetch", nb)(n)),
        t(function() {
            e.forEach(function(n) {
                return n()
            })
        }))
    }
    ]
      , nk = ["resource"]
      , nC = ["longtask"]
      , nO = function(n, t, e) {
        var r = n && new n(function(n, r) {
            n.getEntries ? n.getEntries().forEach(function(n, e, o) {
                return t(n, e, o, r)
            }) : e && e()
        }
        );
        return [function(t) {
            if (!n || !r)
                return e && e();
            try {
                r.observe({
                    entryTypes: t
                })
            } catch (n) {
                return e && e()
            }
        }
        , function(t, o) {
            if (!n || !r)
                return e && e();
            try {
                var i = {
                    type: t,
                    buffered: !0
                };
                void 0 !== o && (i.durationThreshold = o),
                r.observe(i)
            } catch (n) {
                return e && e()
            }
            r.observe({
                type: t,
                buffered: !1
            })
        }
        , function() {
            return r && r.disconnect()
        }
        ]
    }
      , nL = function(n, t, r) {
        return t = (n = e(nO(n, t), 3))[0],
        n = n[2],
        t(r),
        n
    }
      , nM = function(n, t, r, o) {
        return t = (n = e(nO(n, t), 3))[1],
        n = n[2],
        t(r, o),
        n
    }
      , nI = ["longtask_0", function(n, t) {
        var e = G();
        e && t(nL(e, n, nC))
    }
    ]
      , nq = ["resource_0", function(n, t) {
        var e, r = G();
        r && (e = ny(),
        t(nL(r, function(t) {
            e(t.name) || n(t)
        }, nk)))
    }
    ]
      , nA = "pageview"
      , nD = "session"
      , nN = "js_error"
      , nP = "http"
      , nB = "resource_error"
      , nH = "resource"
      , nU = "custom"
      , nW = "performance"
      , nF = "performance_timing"
      , nX = "performance_longtask"
      , nz = "blank_screen"
      , nG = "01"
      , nJ = {
        sampleRate: 1,
        origins: []
    }
      , nY = function() {
        var n = window && (window.crypto || window.msCrypto);
        if (void 0 !== n && n.getRandomValues) {
            var t = new Uint16Array(8);
            return n.getRandomValues(t),
            (n = function(n) {
                for (var t = n.toString(16); t.length < 4; )
                    t = "0" + t;
                return t
            }
            )(t[0]) + n(t[1]) + n(t[2]) + n(t[3]) + n(t[4]) + n(t[5]) + n(t[6]) + n(t[7])
        }
        return "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx".replace(/[x]/g, function() {
            return (16 * Math.random() | 0).toString(16)
        })
    }
      , n$ = RegExp("(cookie|auth|jwt|token|key|ticket|secret|credential|session|password)", "i")
      , nV = RegExp("(bearer|session)", "i")
      , nK = function(n) {
        var t = !1;
        return function(e) {
            t || (t = !0,
            n(e))
        }
    }
      , nQ = function(n, e) {
        try {
            var r;
            e && (r = n.request.url,
            n.request.url = e(r),
            n.extra = t(t({}, n.extra), {
                original_url: r
            }))
        } catch (n) {}
    }
      , nZ = function(n, t) {
        var r, o = n._method, i = n._reqHeaders, u = n._url, a = n._start, c = n._data, i = {
            api: "xhr",
            request: {
                url: J(u),
                method: (o || "").toLowerCase(),
                headers: i && Object.keys(r = i).reduce(function(n, t) {
                    return nw(t, r[t]) || (n[t.toLowerCase()] = r[t]),
                    n
                }, {}),
                timestamp: a
            },
            response: {
                status: n.status || 0,
                is_custom_error: !1,
                timestamp: B()
            },
            duration: B() - a
        };
        "function" == typeof n.getAllResponseHeaders && (i.response.headers = v(f = n.getAllResponseHeaders()) && f ? f.split("\r\n").reduce(function(n, t) {
            var r;
            return v(t) && (nw(t = (r = e(t.split(": "), 2))[0], r = r[1]) || (n[t.toLowerCase()] = r)),
            n
        }, {}) : {});
        var a = i.response.status
          , f = t.collectBodyOnError
          , t = t.extraExtractor;
        try {
            var s = null == t ? void 0 : t(n.response, i, c);
            s && (i.extra = s),
            s && (i.response.is_custom_error = !0),
            f && (s || 400 <= a) && (i.request.body = c ? "" + c : void 0,
            i.response.body = n.response ? "" + n.response : void 0)
        } catch (n) {}
        return i
    };
    function n0(n, t, e) {
        return nh(t = null === (n = n.config()) || void 0 === n ? void 0 : n.plugins[t], e)
    }
    var n1 = "ajax"
      , n2 = {
        autoWrap: !0,
        setContextAtReq: function() {
            return a
        },
        ignoreUrls: [],
        collectBodyOnError: !1
    };
    function n3(n, t) {
        return function(e) {
            if (t)
                try {
                    n(e)
                } catch (n) {}
        }
    }
    var n4 = "click"
      , n5 = ["click_0", function(n, t) {
        var e, r = U();
        r && (e = nd(r, n4, n, !0),
        t(function() {
            e()
        }))
    }
    ]
      , n6 = ["keypress_0", function(n, t) {
        var e, r = U();
        r && (e = nd(r, "keypress", n, !0),
        t(function() {
            e()
        }))
    }
    ]
      , n8 = function(n, o, i) {
        var u, c, f, s, l, d = e(o, 2), p = d[0], v = d[1], h = i.maxBreadcrumbs, m = i.onAddBreadcrumb, g = i.onMaxBreadcrumbs, o = i.dom, d = e(function(n) {
            var t;
            function e(n, e) {
                var r;
                return function(o) {
                    t = void 0,
                    o && r !== o && e({
                        event: r = o,
                        name: n
                    })
                }
            }
            return [e, function(n) {
                return function(r) {
                    try {
                        o = r.target
                    } catch (n) {
                        return
                    }
                    var o, i = o && o.tagName;
                    i && ("INPUT" === i || "TEXTAREA" === i || o.isContentEditable) && (t || e("input", n)(r),
                    clearTimeout(t),
                    t = window.setTimeout(function() {
                        t = void 0
                    }, 100))
                }
            }
            ]
        }(0), 2), i = d[0], d = d[1], m = e((u = h,
        c = m,
        f = g,
        void 0 === u && (u = 20),
        void 0 === c && (c = a),
        void 0 === f && (f = function(n, t) {
            return n.slice(-t)
        }
        ),
        s = [],
        [function() {
            return s
        }
        , function(n) {
            var o = c(n);
            o && (n = t(t({}, o), {
                timestamp: n.timestamp || B()
            }),
            s = 0 <= u && s.length + 1 > u ? f(r(r([], e(s), !1), [n], !1), u) : r(r([], e(s), !1), [n], !1))
        }
        ]), 2), g = m[0], m = m[1];
        return o && (l = m,
        n.push(p[0](i(n4, n3(i = function(n) {
            var t;
            try {
                t = n.event.target ? ns(n.event.target) : ns(n.event)
            } catch (n) {
                t = nf
            }
            0 !== t.length && l({
                type: "dom",
                category: "ui." + n.name,
                message: t
            })
        }
        , "dom")))),
        n.push(v[0](d(n3(i, "dom"))))),
        [g, m]
    }
      , n7 = "breadcrumb"
      , n9 = {
        maxBreadcrumbs: 20,
        dom: !0
    };
    function tn(n, t) {
        return n instanceof t
    }
    function tt(n, t, e) {
        return t = t && t.method || "get",
        (t = tn(n, e) && n.method || t).toLowerCase()
    }
    function te(n) {
        for (var t = [], e = 1; e < arguments.length; e++)
            t[e - 1] = arguments[e];
        try {
            return t.reduce(function(t, e) {
                return new n(e || {}).forEach(function(n, e) {
                    return !nw(e, n) && (t[e] = n)
                }),
                t
            }, {})
        } catch (n) {
            return {}
        }
    }
    function tr(n, t, e) {
        return tn(n, e) ? n.body : null == t ? void 0 : t.body
    }
    var to = function(n) {
        if (!v(n))
            return !1;
        var t = e(n.split(":"), 2)
          , n = t[0];
        return !t[1] || "http" === n || "https" === n
    }
      , ti = function(n, e, r, o, i, u) {
        tn(r, i) ? r.headers.set(n, e) : o.headers instanceof u ? o.headers.set(n, e) : o.headers = t(t({}, o.headers), ((o = {})[n] = e,
        o))
    }
      , tu = function(n, t, e, r, o, i, a) {
        function c() {
            var e;
            s && (f.request.body = null === (e = tr(n, t, r)) || void 0 === e ? void 0 : e.toString())
        }
        var f = {
            api: "fetch",
            request: {
                method: tt(n, t, r),
                timestamp: a,
                url: J(n instanceof r ? n.url : n),
                headers: te(o, n.headers, t.headers)
            },
            response: {
                status: e && e.status || 0,
                is_custom_error: !1,
                timestamp: B()
            },
            duration: B() - a
        }
          , s = i.collectBodyOnError
          , l = i.extraExtractor;
        if (e)
            try {
                var d = te(o, e.headers);
                f.response.headers = d;
                try {
                    -1 !== (d["content-type"] || "").indexOf("application/json") && l && e.clone().json().then(function(e) {
                        (e = l(e, f, null === (e = tr(n, t, r)) || void 0 === e ? void 0 : e.toString())) && (f.extra = e,
                        f.response.is_custom_error = !0,
                        c())
                    }).catch(u)
                } catch (n) {}
                400 <= e.status && c()
            } catch (n) {}
        else
            c();
        return f
    }
      , ta = "fetch"
      , tc = {
        autoWrap: !0,
        setContextAtReq: function() {
            return a
        },
        ignoreUrls: [],
        collectBodyOnError: !1
    };
    function tf(n) {
        var t;
        return !function(n) {
            switch (Object.prototype.toString.call(n)) {
            case "[object Error]":
            case "[object Exception]":
            case "[object DOMError]":
            case "[object DOMException]":
                return 1;
            default:
                return n instanceof Error
            }
        }(n) ? (s(n) || "undefined" != typeof Event && function(n, t) {
            try {
                return n instanceof t
            } catch (n) {
                return
            }
        }(n, Event) || v(n)) && (t = {
            message: _(n)
        }) : t = n && c(n) ? td.reduce(function(t, e) {
            return t[e] = n[e],
            t
        }, {}) : n,
        t
    }
    function ts(n) {
        var t = tf(n.error);
        if (!t)
            return t;
        var e = n.colno
          , r = n.lineno
          , n = n.filename;
        return e && !t.colno && (t.colno = String(e)),
        r && !t.lineno && (t.lineno = String(r)),
        n && !t.filename && (t.filename = n),
        t
    }
    function tl(n) {
        var e;
        try {
            var r = void 0;
            if ("reason"in n ? r = n.reason : "detail"in n && "reason"in n.detail && (r = n.detail.reason),
            r) {
                var o = tf(r);
                return t(t({}, o), {
                    name: null !== (e = o && o.name) && void 0 !== e ? e : "UnhandledRejection"
                })
            }
        } catch (n) {}
    }
    var td = ["name", "message", "stack", "filename", "lineno", "colno"]
      , tp = ["EventTarget", "Window", "Node", "ApplicationCache", "ChannelMergerNode", "EventSource", "FileReader", "HTMLUnknownElement", "IDBDatabase", "IDBRequest", "IDBTransaction", "MessagePort", "Notification", "SVGElementInstance", "Screen", "TextTrack", "TextTrackCue", "TextTrackList", "WebSocket", "Worker", "XMLHttpRequest", "XMLHttpRequestEventTarget", "XMLHttpRequestUpload"]
      , tv = ["setTimeout", "setInterval", "requestAnimationFrame", "requestIdleCallback"]
      , th = ["onload", "onerror", "onprogress", "onreadystatechange"]
      , tm = "addEventListener"
      , tg = ["async_error_0", function(n, o) {
        function i(e, r) {
            if (!d(e))
                return e;
            var o = {
                type: "capture-global",
                data: t({}, r)
            }
              , u = e._w_ || (e._w_ = function() {
                try {
                    return (e.handleEvent && d(e.handleEvent) ? e.handleEvent : e).apply(this, [].map.call(arguments, function(n) {
                        return i(n, r)
                    }))
                } catch (e) {
                    var t = tf(e);
                    throw t && n({
                        source: o,
                        error: t
                    }),
                    e
                }
            }
            );
            return u._hook_ = !0,
            u
        }
        var u = H()
          , a = X()
          , c = [];
        u && c.push.apply(c, r([], e(tv.filter(function(n) {
            return u[n]
        }).map(function(n) {
            return w(u, n, function(t) {
                return function(o) {
                    for (var u = [], a = 1; a < arguments.length; a++)
                        u[a - 1] = arguments[a];
                    return t && t.call.apply(t, r([this, i(o, {
                        function: n
                    })], e(u), !1))
                }
            }, !1)()
        })), !1)),
        a && a.prototype && c.push(w(a.prototype, "send", function(n) {
            return function() {
                for (var t = this, e = [], r = 0; r < arguments.length; r++)
                    e[r] = arguments[r];
                return th.filter(function(n) {
                    return t[n] && !t[n]._hook_
                }).forEach(function(n) {
                    t[n] = i(t[n], {
                        function: n
                    })
                }),
                n.apply(this, e)
            }
        }, !1)()),
        tp.forEach(function(n) {
            var t = u && u[n] && u[n].prototype;
            t && t[tm] && (c.push(w(t, tm, function(t) {
                return function(e, r, o) {
                    try {
                        var u = r.handleEvent;
                        d(u) && (r.handleEvent = i(u, {
                            function: "handleEvent",
                            target: n
                        }))
                    } catch (n) {}
                    return t && t.call(this, e, i(r, {
                        function: tm,
                        target: n
                    }), o)
                }
            }, !1)()),
            c.push(w(t, "removeEventListener", function(n) {
                return function(t, e, r) {
                    return null != e && e._w_ && n.call(this, t, e._w_, r),
                    n.call(this, t, e, r)
                }
            }, !1)()))
        }),
        o(function() {
            return c.forEach(function(n) {
                return n()
            })
        })
    }
    ]
      , ty = ["err_0", function(n, t) {
        var e, r = H();
        r && (e = nl(r, "error", n, !0),
        t(function() {
            e()
        }))
    }
    ]
      , tb = ["perr_0", function(n, t) {
        var e, r = H();
        r && (e = nl(r, "unhandledrejection", n, !0),
        t(function() {
            e()
        }))
    }
    ]
      , t_ = function(n, t, r, o) {
        function i(t) {
            var e = t.error
              , r = t.extra
              , o = t.react
              , t = t.source;
            !(e = d ? v(e) : e) || !e.message || p && p.test(e.message) || n({
                ev_type: nN,
                payload: {
                    error: e,
                    breadcrumbs: [],
                    extra: r,
                    react: o,
                    source: t
                }
            })
        }
        var u, a = e(r, 3), c = a[0], f = a[1], s = a[2], l = o.ignoreErrors, r = o.onerror, a = o.onunhandledrejection, d = o.dedupe, o = o.captureGlobalAsync, p = y(l), v = function(n) {
            var t, e, r, o, i;
            try {
                if (t = u,
                !(!n || !t) && (e = n.message,
                r = t.message,
                e && r && e === r && (o = n.stack,
                i = t.stack,
                o && i && o === i)))
                    return void (u = n)
            } catch (n) {
                V(n)
            }
            return u = n
        };
        return r && t.push(c[0](function(n) {
            return i({
                error: ts(n),
                source: {
                    type: "onerror"
                }
            })
        })),
        a && t.push(f[0](function(n) {
            return i({
                error: tl(n),
                source: {
                    type: "onunhandledrejection"
                }
            })
        })),
        o && t.push(s()[0](function(n) {
            i(n)
        })),
        function(n, t, e) {
            return i({
                error: "[object ErrorEvent]" === Object.prototype.toString.call(n) ? ts(n) : ("[object PromiseRejectionEvent]" === Object.prototype.toString.call(n) ? tl : tf)(n),
                extra: t,
                react: e,
                source: {
                    type: "manual"
                }
            })
        }
    }
      , tw = "jsError"
      , tx = {
        ignoreErrors: [],
        onerror: !0,
        onunhandledrejection: !0,
        captureGlobalAsync: !1,
        dedupe: !0
    };
    function tE(n) {
        return "complete" === n.readyState
    }
    function tS(n, t) {
        var e = n[0] + n[1] + n[2]
          , r = n[0] / e;
        return n[2] / e > t.frustrating_threshold ? 2 : r > t.satisfying_threshold || 0 === e ? 0 : 1
    }
    function tT(n, t) {
        return function(e, r) {
            var o = e.payload;
            switch (e.ev_type) {
            case nW:
                var i = o.name;
                o.isSupport && n(r[tB], i, o.value);
                break;
            case "action":
                n(r[tB], "action", o.duration || 0);
                break;
            case nN:
                t(r[tN], 0);
                break;
            case nP:
                o.response.is_custom_error || 400 <= o.response.status ? t(r[tN], 1) : (i = o.response.timing) && n(r[tP], 0, i.duration);
                break;
            case nB:
                t(r[tN], 2);
                break;
            case nz:
                t(r[tN], 3);
                break;
            case nH:
                n(r[tP], 1, o.duration);
                break;
            case nX:
                o.longtasks.forEach(function(t) {
                    n(r[tP], 2, t.duration)
                })
            }
        }
    }
    function tR() {
        var n, t;
        function e() {
            n = [0, 0, 0],
            t = {
                error_count: [0, 0, 0, 0],
                duration_count: [0, 0, 0],
                perf_apdex: {}
            }
        }
        return e(),
        [function(e, r, o) {
            var i = e && e[r];
            !i || o <= 0 || (e = o < (i[0].threshold || 0) ? 0 : o > (i[1].threshold || 0) ? 2 : 1,
            n[e] += i[e].weight,
            "string" == typeof r ? (i = t[tB][o = r + "_" + e],
            t[tB][o] = (i || 0) + 1) : 2 == e && (t.duration_count[r] += 1))
        }
        , function(e, r) {
            e && (n[2] += e[r],
            t.error_count[r] += 1)
        }
        , function() {
            return [n, t]
        }
        , e]
    }
    var tj = function(n) {
        return "hidden" === n.visibilityState
    }
      , tk = ["hidden_3", function(n, t) {
        var e, r, o, i = U(), u = H();
        i && u && (r = nd(i, "visibilitychange", e = function(t) {
            n("pagehide" === t.type || tj(i))
        }
        , !0),
        o = nl(u, "pagehide", e, !0),
        t(function() {
            r(),
            o()
        }, function(n) {
            n(tj(i))
        }))
    }
    ]
      , tC = ["load_1", function(n, t) {
        var e, r, o, i = H(), a = U();
        i && a && (e = !1,
        r = u,
        o = function() {
            setTimeout(function() {
                n(),
                e = !0
            }, 0)
        }
        ,
        tE(a) ? o() : r = nl(i, "load", o, !1),
        t(function() {
            r()
        }, function(n) {
            e && n()
        }))
    }
    ]
      , tO = ["unload_0", function(n, t) {
        var r, o, i, u = H();
        u && (r = e(nv(n), 1)[0],
        o = function() {
            r()
        }
        ,
        i = [],
        ["unload", "beforeunload", "pagehide"].forEach(function(n) {
            i.push(nl(u, n, o, !1))
        }),
        t(function() {
            i.forEach(function(n) {
                return n()
            })
        }))
    }
    ]
      , tL = ["domLoad_1", function(n, t) {
        var e, r, o = H(), i = U();
        o && i && (e = !1,
        r = u,
        o = function() {
            setTimeout(function() {
                n(),
                e = !0
            }, 0)
        }
        ,
        "loading" !== i.readyState ? o() : r = nd(i, "DOMContentLoaded", o, !1),
        t(function() {
            r()
        }, function(n) {
            e && n()
        }))
    }
    ]
      , tM = ["activated_0", function(n, t) {
        var e, r, o, i = U();
        i && (e = !1,
        r = u,
        o = function() {
            n(),
            e = !0
        }
        ,
        i && i.prerendering ? r = nd(i, "prerenderingchange", o, !0) : o(),
        t(function() {
            r()
        }, function(n) {
            e && n()
        }))
    }
    ]
      , tI = ["hash_0", function(n, t) {
        var e, r = H();
        r && (e = nl(r, "hashchange", function() {
            return n(location.href)
        }, !0),
        t(function() {
            e()
        }))
    }
    ]
      , tq = ["history_0", function(n, t) {
        var e, r, o, i = H() && window.history, u = H();
        i && u && (r = function() {
            return n(location.href)
        }
        ,
        (e = []).push(w(i, "pushState", o = function(n) {
            return function() {
                for (var t = [], e = 0; e < arguments.length; e++)
                    t[e] = arguments[e];
                try {
                    n.apply(i, t)
                } finally {
                    r()
                }
            }
        }
        )(), w(i, "replaceState", o)()),
        e.push(nl(u, "popstate", r, !0)),
        t(function() {
            e.forEach(function(n) {
                return n()
            })
        }))
    }
    ]
      , tA = function(n) {
        return n + "_" + B()
    }
      , tD = function(n) {
        return "manual" === n
    }
      , tN = "error_weight"
      , tP = "duration_apdex"
      , tB = "perf_apdex"
      , tH = function(n, t, r, o) {
        var i, u, a, c, f, s, l, d, p, v, h = o.sendInit, m = o.initPid, g = o.routeMode, y = o.extractPid, o = o.onPidUpdate, b = tD(g) ? function() {
            return ""
        }
        : function(n) {
            var t;
            return "hash" === g ? (null === (t = Y(n).hash) || void 0 === t ? void 0 : t.replace(/^#/, "")) || "/" : Y(n).path
        }
        , _ = y || function() {}
        , o = e((i = function(t, e) {
            n({
                ev_type: nA,
                payload: {
                    pid: e,
                    source: t
                }
            })
        }
        ,
        u = m || (null !== (d = _(l = location.href)) && void 0 !== d ? d : b(l)),
        a = b(location.href),
        c = o,
        f = a,
        s = u,
        c && c(u),
        [function(n, t, e) {
            "user_set" !== n && t !== f ? (f = t,
            s = null != e ? e : f,
            c && c(s),
            i(n, s)) : "user_set" === n && t !== s && (s = t,
            c && c(s),
            i(n, s))
        }
        , function() {
            u && i("init", u)
        }
        ]), 2), w = o[0], o = o[1];
        return tD(g) || (p = e((v = "",
        [function(n, t) {
            var e;
            t !== v && w(n, b(e = v = t), _(e))
        }
        ]), 1)[0],
        r.length && r.forEach(function(n) {
            return t.push(n[0](function(n) {
                return p(g, n)
            }))
        })),
        h && o(),
        [w.bind(null, "user_set")]
    }
      , tU = function(n, t, r, o) {
        var i, u, a, c = e(r, 2), f = c[0], s = c[1], l = 2 === o.apdex, d = void 0, p = void 0, v = void 0, h = !1, m = e(tR(), 4), g = m[0], y = m[1], b = m[2], _ = m[3], r = e(tR(), 4), c = r[0], o = r[1], w = r[2], x = r[3], m = e((i = {
            start: B(),
            end: 0,
            time_spent: 0,
            is_bounced: !1,
            entry: "",
            exit: "",
            p_count: 0,
            a_count: 0
        },
        [function(n, t) {
            var r = e(n, 3)
              , o = r[0]
              , n = r[1]
              , r = r[2];
            i.end = B(),
            i.time_spent += t && t.time_spent || 0,
            i.last_page = t,
            i.p_count += 1,
            i.rank = o,
            i.apdex = n,
            i.apdex_detail = r,
            (r = U()) && (i.is_bounced = !tE(r))
        }
        , function(n, t) {
            i.time_spent += n.time_spent,
            i.p_count += 1,
            i.exit = t
        }
        , function() {
            i.a_count += 1
        }
        , function(n) {
            i.entry = n,
            i.exit = n
        }
        , function() {
            return i
        }
        ]), 5), E = m[0], S = m[1], T = m[2], R = m[3], j = m[4], r = e((a = void (u = 0),
        [function(n) {
            n ? a && (u += B() - a,
            a = void 0) : a = B()
        }
        , function() {
            a && (u += B() - a);
            var n = u;
            return u = 0,
            a = B(),
            n
        }
        ]), 2), m = r[0], k = r[1];
        t.push(f[0](m)),
        l || t.push(s[0](function() {
            var t, r, o;
            h && (t = (o = e(w(), 2))[0],
            r = o[1],
            E([o = tS(t, v), t, r], L()),
            n({
                ev_type: nD,
                payload: j()
            }),
            x())
        }));
        var C = tT(g, y)
          , O = tT(c, o)
          , L = function() {
            var n = e(b(), 2)
              , t = n[0]
              , n = n[1];
            return {
                start: d[0],
                pid: d[1],
                view_id: d[2],
                end: B(),
                time_spent: k(),
                apdex: t,
                rank: tS(t, v),
                detail: n
            }
        };
        return t.push(function() {
            h = !1
        }),
        [function(n, t) {
            if (!d)
                return d = [B(), n, t],
                R(n),
                void (h = !(!v || !d));
            h && S(p = L(), n),
            d = [B(), n, t],
            _()
        }
        , function(n) {
            h && (l || (O(n, v),
            "action" === n.ev_type && T()),
            n.common.pid === d[1] && C(n, v))
        }
        , function(t) {
            h && (t.payload.last = p),
            n(t)
        }
        , function(n) {
            if (!n)
                return t.forEach(function(n) {
                    return n()
                }),
                void (t.length = 0);
            h = !(!(v = n) || !d)
        }
        ]
    }
      , tW = "pageview"
      , tF = {
        sendInit: !0,
        routeMode: "history",
        apdex: 2
    }
      , tX = ["xmlhttprequest", "fetch", "beacon"]
      , tz = function(n, t, r, o) {
        var i, u, a, c, f = e(r, 2), r = f[0], s = f[1], l = F();
        l && (f = o.ignoreUrls,
        i = o.slowSessionThreshold,
        u = o.ignoreTypes,
        a = y(f),
        c = function(t, e) {
            void 0 === e && (e = !1),
            h(u || tX, t.initiatorType) || a && a.test(t.name) || (t = {
                ev_type: nH,
                payload: t
            },
            e && (t.extra = {
                sample_rate: 1
            }),
            n(t))
        }
        ,
        t.push(r[0](function() {
            var n = e(nu(l), 3)
              , r = n[0]
              , n = n[2]
              , o = !!r && i < r.loadEventEnd - r.navigationStart;
            n("resource").forEach(function(n) {
                return c(n, o)
            }),
            t.push(s()[0](function(n) {
                c(n)
            }))
        })))
    }
      , tG = "resource"
      , tJ = {
        ignoreUrls: [],
        slowSessionThreshold: 4e3
    }
      , tY = function(n, t) {
        var e, r, o = n.target || n.srcElement;
        if (o && (n = o.tagName) && v(n))
            return {
                url: (e = "link" === (r = e = o).tagName.toLowerCase() ? "href" : "src",
                d(r.getAttribute) ? r.getAttribute(e) || "" : r[e] || ""),
                tagName: n,
                xpath: t ? ns(o) : void 0
            }
    }
      , t$ = function(n, t) {
        var e = n.url
          , r = n.tagName
          , n = n.xpath
          , e = J(e)
          , t = t(e)[0];
        return {
            type: r.toLowerCase(),
            url: e,
            xpath: n,
            timing: t
        }
    }
      , tV = "resourceError"
      , tK = {
        includeUrls: [],
        ignoreUrls: [],
        dedupe: !0,
        gatherPath: !1
    };
    function tQ(n) {
        return function(t, e) {
            n(t2(t, e))
        }
    }
    var tZ = {
        isSupport: !0,
        isPolyfill: !1,
        isBounced: !1,
        isCustom: !1,
        type: "perf"
    }
      , t0 = function(n, e) {
        return t({
            name: n,
            value: e
        }, tZ)
    }
      , t1 = function(n, t, e) {
        var r = !1;
        return function(o) {
            e.length && e.forEach(function(n) {
                n()
            }),
            e.length = 0,
            r || (r = !0,
            t && t(n(o)))
        }
    }
      , t2 = function(n, t) {
        return {
            ev_type: nW,
            payload: n,
            overrides: t
        }
    }
      , t3 = function() {
        var n = (0,
        e(nu(F()), 3)[2])("navigation")[0];
        return n && n.activationStart || 0
    };
    function t4(n) {
        var n = (t = n || {}).domContentLoadedEventEnd
          , t = t.navigationStart;
        return n ? n - (void 0 === t ? 0 : t) : null
    }
    function t5(n, t) {
        var e = n.startTime
          , r = n.duration;
        n.start = e,
        n.end = e + r,
        t.push(n)
    }
    var t6 = function(n) {
        var t, e, r, o, i, u, a, c = n.previousRect, f = n.currentRect, s = window.innerWidth * window.devicePixelRatio, l = window.innerHeight * window.devicePixelRatio;
        return t = Math.max(f.left, c.left),
        e = Math.min(f.right, c.right),
        r = Math.max(f.top, c.top),
        r = Math.min(f.bottom, c.bottom) - r,
        r = (t = e - t) <= 0 || r <= 0 ? 0 : t * r,
        Math.min((f.width * f.height + c.width * c.height - r) / (l * s), 1) * (i = (o = 0 === f.x && 0 === f.y && 0 === f.width && 0 === f.height ? {
            x: f.x,
            y: l
        } : {
            x: f.x,
            y: f.y
        }).x,
        u = o.y,
        Math.min((u = Math.max(Math.abs(i - (o = (a = 0 === c.x && 0 === c.y && 0 === c.width && 0 === c.height ? {
            x: c.x,
            y: l
        } : {
            x: c.x,
            y: c.y
        }).x)), Math.abs(u - (a = a.y)))) / (a = Math.max(s, l)), 1))
    }
      , t8 = "first-contentful-paint"
      , t7 = "first-paint"
      , t9 = function(n, t, r, o, i) {
        var i = e(i, 3)
          , u = i[0]
          , a = i[1]
          , c = i[2]
          , f = G()
          , s = F()
          , l = U()
          , d = t0(t, 0)
          , p = t1(t2, r, o);
        if (!s || !f || !l)
            return d.isSupport = !1,
            void p(d);
        function v() {
            if (tj(l))
                return d.isSupport = !1,
                void p(d);
            function t(n) {
                var t = n.startTime
                  , n = t3();
                d.value = t < n ? 0 : t - n,
                p(d)
            }
            var r, i, u = (0,
            e(nu(s), 5)[4])(n)[0];
            u ? t(u) : (o.push(nL(f, function(e) {
                e.name === n && t(e)
            }, ["paint"])),
            u = c(),
            o.push(u[0](function() {
                d.isBounced = !0,
                p(d)
            })),
            r = function(n) {
                n && p(d)
            }
            ,
            i = a(),
            o.push(function() {
                return i[1](r)
            }),
            i[0](r))
        }
        o.push(function() {
            return u[1](v)
        }),
        u[0](v)
    }
      , en = ["fp", function(n, t, e) {
        return t9(t7, "fp", n, t, e)
    }
    ]
      , et = ["fcp", function(n, t, e) {
        return t9(t8, "fcp", n, t, e)
    }
    ]
      , ee = function(n, t, r, o) {
        var i, a, c, f, s, l, d = e(r, 5), p = d[0], v = d[1], m = d[2], g = d[3], y = d[4], b = t0("tti", 0), _ = t1(t2, n, t), r = F(), d = G(), n = o || {}, o = n.entries, w = void 0 === o ? [] : o, x = n.observer;
        if (t.push(function() {
            x && x.disconnect(),
            w.length = 0
        }),
        !window || !XMLHttpRequest || !r || !d || d.supportedEntryTypes && !h(d.supportedEntryTypes || [], nC[0]))
            return b.isSupport = !1,
            void _(b);
        var n = e(nu(r), 5)
          , E = n[0]
          , S = n[1]
          , T = n[4]
          , d = e(function(n) {
            function t(t) {
                t < r || !e || (i(),
                o = window.setTimeout(e, t - n()),
                r = t)
            }
            var e, r = -1 / 0, o = void 0, i = function() {
                return window.clearTimeout(o)
            };
            return [function(n, r) {
                e = n,
                t(r)
            }
            , function() {
                i(),
                e = void 0
            }
            , t]
        }(S), 3)
          , r = d[0]
          , n = d[1]
          , R = d[2]
          , g = e((a = (i = e(i = [p, v, m, g, z()], 5))[0],
        c = i[1],
        f = i[2],
        s = i[3],
        l = i[4],
        function(n, r) {
            var o, i, d, p, v = [], m = [], g = e([p = {}, function(n, t) {
                return p[n] = t
            }
            , function(n) {
                return delete p[n]
            }
            ], 3), y = g[0], b = g[1], _ = g[2];
            w.forEach(function(n) {
                n.entryType === nC[0] && t5(n, v)
            });
            var x = 0;
            t.push(a[0](function(n) {
                if ("get" !== (e(n, 1)[0] || "").toLowerCase())
                    return u;
                var t = x += 1;
                return b(t, B()),
                function() {
                    _(t)
                }
            })),
            t.push(c[0](function(n) {
                var t = e(n, 2)
                  , n = t[0]
                  , t = t[1];
                if (!window.Request || "get" !== tt(n, t, window.Request))
                    return u;
                var r = x += 1;
                return b(r, B()),
                function() {
                    _(r)
                }
            }));
            var E = e(l && (i = ["img", "script", "iframe", "link", "audio", "video", "source"],
            d = (o = e(K(o = l, function(t) {
                for (var e = 0; e < t.length; e++)
                    ("childList" === t[e].type && function n(t, e) {
                        for (var r = 0; r < t.length; r++)
                            if (h(e, t[r].nodeName.toLowerCase()) || t[r].children && n(t[r].children, e))
                                return 1
                    }(t[e].addedNodes, i) || "attributes" === t[e].type && h(i, t[e].target.nodeName.toLowerCase())) && (t[e],
                    n(r() + 5e3))
            }), 2))[0],
            [function() {
                return d(document, {
                    attributes: !0,
                    childList: !0,
                    subtree: !0,
                    attributeFilter: ["href", "src"]
                })
            }
            , o[1]]) || [], 2)
              , g = E[0]
              , E = E[1];
            function S() {
                return function(n, t, r) {
                    if (2 < n.length)
                        return r();
                    for (var o = [], i = 0; i < t.length; i++)
                        o.push([t[i].start, 0], [t[i].end, 1]);
                    for (i = 0; i < n.length; i++)
                        o.push([n[i], 0]);
                    o.sort(function(n, t) {
                        return n[0] - t[0]
                    });
                    for (var u = n.length, i = o.length - 1; 0 <= i; i--) {
                        var a = e(o[i], 2)
                          , c = a[0];
                        switch (a[1]) {
                        case 0:
                            u--;
                            break;
                        case 1:
                            if (2 < ++u)
                                return c
                        }
                    }
                    return 0
                }(function(n) {
                    for (var t = Object.keys(n), e = [], r = 0; r < t.length; r++) {
                        var o = n[t[r]];
                        "number" == typeof o && e.push(o)
                    }
                    return e
                }(y), m, r)
            }
            return g && g(),
            E && t.push(E),
            t.push(f[0](function(t) {
                t5(t, v);
                var e = t.startTime
                  , t = t.duration;
                n(e + t + 5e3)
            })),
            t.push(s[0](function(t) {
                var e = t.fetchStart
                  , t = t.responseEnd;
                m.push({
                    start: e,
                    end: t
                }),
                n(S() + 5e3)
            })),
            t.push(function() {
                v.length = 0,
                m.length = 0
            }),
            [v, S]
        }
        )(R, S), 2)
          , j = g[0]
          , k = g[1];
        function C(n) {
            b.value = n,
            _(b)
        }
        t.push(n),
        n = j[j.length - 1],
        r(function() {
            return function(n) {
                var t, e, r, o, i, u = T(t8)[0];
                if (t = (u ? u.startTime : t4(E)) || 0,
                e = t4(E) || 0,
                r = k(),
                o = S(),
                i = j,
                !(u = o - r < 5e3 ? null : o - (i = 0 === i.length ? t : i[i.length - 1].end) < 5e3 ? null : Math.max(i, e)))
                    return R(S() + 1e3);
                n(u)
            }(C)
        }, Math.max(k() + 5e3, n ? n.end : 0)),
        t.push(y[0](function() {
            b.isSupport = !1,
            _(b)
        }))
    }
      , er = ["SCRIPT", "STYLE", "META", "HEAD"]
      , eo = function(n, t, r) {
        var o = e(r, 2)
          , i = o[0]
          , a = o[1]
          , c = U()
          , f = z()
          , s = F()
          , l = s && s.timing && s.timing.navigationStart || void 0
          , p = t0("fmp", 0)
          , v = t1(t2, n, t);
        if (!c || !f || !l)
            return p.isSupport = !1,
            void v(p);
        function h() {
            return _.push({
                time: B() - b,
                score: function n(t, e, r, o) {
                    if (!t || -1 < o.indexOf(t.tagName))
                        return 0;
                    var i = t.children;
                    return (i = [].slice.call(void 0 === i ? [] : i).reduceRight(function(t, r) {
                        return t + n(r, e + 1, 0 < t, o)
                    }, 0)) <= 0 && !r && (!d(t.getBoundingClientRect) || (t = (r = t.getBoundingClientRect() || {}).top,
                    r = r.height,
                    t > window.innerHeight || r <= 0)) ? 0 : i + 1 + .5 * e
                }(c && c.body, 1, !1, er)
            })
        }
        var m, g, y, b = B(), _ = [], r = function() {
            if (H() && "requestAnimationFrame"in window)
                return window.requestAnimationFrame
        }(), o = function() {
            if (H() && "cancelAnimationFrame"in window)
                return window.cancelAnimationFrame
        }(), w = e((s = c,
        n = o,
        o = !0,
        [function(n) {
            m && y(m),
            m = g(n)
        }
        , g = !d(r) || o && s && s.hidden ? function(n) {
            return n(0),
            0
        }
        : r, y = d(n) ? n : u]), 1)[0], n = e(K(f, function() {
            return w(h)
        }), 2), f = n[0], n = n[1], x = b - (l || 0);
        f(c, {
            subtree: !0,
            childList: !0
        }),
        t.push(n),
        t.push(a[0](function() {
            p.isSupport = !1,
            v(p)
        })),
        t.push(i[0](function() {
            var n;
            (n = window.setTimeout(function() {
                var n, t, r;
                void 0 === (n = x) && (n = 0),
                r = (t = e(void 0 === (r = _) ? [] : r))[0],
                p.value = (r = (t = t.slice(1)) && t.reduce(function(n, t) {
                    var r = e(n, 2)
                      , o = r[0]
                      , n = r[1]
                      , r = t.score - o.score;
                    return [t, t.time >= o.time && n.rate < r ? {
                        time: t.time,
                        rate: r
                    } : n]
                }, [r, {
                    time: null == r ? void 0 : r.time,
                    rate: 0
                }])[1].time || 0) ? r + n : 0,
                v(p),
                _.length = 0
            }, 200)) && t.push(function() {
                return clearTimeout(n)
            })
        }))
    }
      , ei = {
        renderType: "CSR"
    }
      , eu = ["keydown", "click"]
      , ea = ["lcp", function(n, t, r) {
        var r = e(r, 3)
          , o = r[0]
          , i = r[1]
          , u = r[2]
          , a = G()
          , c = U()
          , f = t0("lcp", 0)
          , s = t1(t2, n, t);
        if (!a || !c)
            return f.isSupport = !1,
            void s(f);
        function l() {
            if (tj(c))
                return f.isSupport = !1,
                void s(f);
            function n() {
                setTimeout(function() {
                    s(f)
                }, 0)
            }
            t.push(nM(a, function(n) {
                var t = n.startTime
                  , e = n.element
                  , n = t3();
                if (f.value = t < n ? 0 : t - n,
                e)
                    try {
                        f.extra = {
                            element: ns(e)
                        }
                    } catch (n) {}
            }, "largest-contentful-paint")),
            eu.forEach(function(e) {
                t.push(nd(c, e, n, !0))
            });
            var e = u();
            function r(n) {
                n && s(f)
            }
            t.push(e[0](function() {
                f.isBounced = !0,
                s(f)
            }));
            var o = i();
            t.push(function() {
                return o[1](r)
            }),
            o[0](r)
        }
        t.push(function() {
            return o[1](l)
        }),
        o[0](l)
    }
    ]
      , ec = ["cls", function(n, t, r) {
        var o = e(r, 4)
          , i = o[1]
          , u = o[2]
          , r = o[3]
          , o = G()
          , a = t0("cls", 0)
          , c = tQ(n);
        if (!o)
            return a.isSupport = !1,
            void c(a);
        var f, s, l, n = e((s = [],
        l = void (f = 0),
        [function() {
            f = 0
        }
        , function(n, t) {
            var e, r;
            t.hadRecentInput || (e = s[0],
            r = s[s.length - 1],
            l = f && t.startTime - r < 1e3 && t.startTime - e < 5e3 ? (f += t.value,
            s.push(t.startTime),
            t.value > l.value ? t : l) : (f = t.value,
            s = [t.startTime],
            t),
            n(f, l))
        }
        ]), 2), d = n[0], n = n[1].bind(null, function(n, t) {
            if (n > a.value) {
                a.value = n;
                try {
                    var e = function(n) {
                        var t, e, n = null === (n = null == n ? void 0 : n.sources) || void 0 === n ? void 0 : n.filter(function(n) {
                            return !!n.node
                        });
                        if (n && n.length) {
                            if (1 === n.length)
                                return n[0].node;
                            var r, o = 0;
                            try {
                                for (var i = function(n) {
                                    var t = "function" == typeof Symbol && Symbol.iterator
                                      , e = t && n[t]
                                      , r = 0;
                                    if (e)
                                        return e.call(n);
                                    if (n && "number" == typeof n.length)
                                        return {
                                            next: function() {
                                                return {
                                                    value: (n = n && r >= n.length ? void 0 : n) && n[r++],
                                                    done: !n
                                                }
                                            }
                                        };
                                    throw TypeError(t ? "Object is not iterable." : "Symbol.iterator is not defined.")
                                }(n), u = i.next(); !u.done; u = i.next()) {
                                    var a = u.value
                                      , c = t6(a);
                                    o < c && (o = c,
                                    r = a.node)
                                }
                            } catch (n) {
                                t = {
                                    error: n
                                }
                            } finally {
                                try {
                                    u && !u.done && (e = i.return) && e.call(i)
                                } finally {
                                    if (t)
                                        throw t.error
                                }
                            }
                            return r
                        }
                    }(t);
                    a.extra = e ? {
                        element: ns(e)
                    } : void 0
                } catch (n) {}
            }
        });
        t.push(nM(o, n, "layout-shift")),
        i = i(),
        t.push(i[0](function(n) {
            n && d()
        })),
        r = r(),
        t.push(r[0](function(n) {
            c(a, n),
            d(),
            a = t0("cls", 0)
        })),
        u = u(),
        t.push(u[0](function() {
            c(a)
        }))
    }
    ]
      , ef = "event"
      , es = ["inp", function(n, t, r) {
        var o = e(r, 4)
          , r = o[0]
          , i = o[2]
          , u = o[3]
          , a = G()
          , c = function() {
            if (H() && d(window.PerformanceEventTiming))
                return window.PerformanceEventTiming
        }()
          , o = F()
          , f = t0("inp", 0)
          , s = tQ(n);
        if (!a || !c || !o)
            return f.isSupport = !1,
            void s(f);
        function l() {
            b = x(),
            _ = [],
            w = {}
        }
        function p(n) {
            var t = _[_.length - 1]
              , e = w[n.interactionId];
            (e || _.length < 10 || n.duration > t.latency) && (e ? (e.entries.push(n),
            e.latency = Math.max(e.latency, n.duration)) : (w[(n = {
                id: n.interactionId,
                latency: n.duration,
                entries: [n]
            }).id] = n,
            _.push(n)),
            _.sort(function(n, t) {
                return t.latency - n.latency
            }),
            _.splice(10).forEach(function(n) {
                delete w[n.id]
            }))
        }
        function v() {
            var n = (n = Math.min(_.length - 1, Math.floor(E() / 50)),
            _[n]);
            n && (f.value = n.latency,
            (n = n.entries[0].target) && (f.extra = {
                element: ns(n)
            }))
        }
        function h(n) {
            n.interactionId && p(n),
            "first-input" !== n.entryType || _.some(function(t) {
                return t.entries.some(function(t) {
                    return n.duration === t.duration && n.startTime === t.startTime
                })
            }) || p(n)
        }
        var m, g, y, b = 0, _ = [], w = {}, x = e((g = 1 / (m = 0),
        y = 0,
        t.push(nM(a, function(n) {
            n.interactionId && (g = Math.min(g, n.interactionId),
            m = (y = Math.max(y, n.interactionId)) ? (y - g) / 7 + 1 : 0)
        }, ef, 0)),
        [function() {
            return m
        }
        ]), 1)[0], E = function() {
            return x() - b
        };
        t.push(r[0](function() {
            t.push(nM(a, h, ef, 40)),
            "interactionId"in c.prototype && t.push(nM(a, h, "first-input"));
            var n = u();
            t.push(n[0](function(n) {
                v(),
                s(f, n),
                l(),
                f = t0("inp", 0)
            })),
            n = i(),
            t.push(n[0](function() {
                v(),
                s(f)
            })),
            t.push(l)
        }))
    }
    ]
      , el = "longtask"
      , ed = [el, function(n, t, r) {
        r = e(r, 4)[3],
        t.push(r[0](function(t) {
            n({
                ev_type: nX,
                payload: {
                    type: "perf",
                    longtasks: [t]
                }
            })
        }))
    }
    ]
      , ep = ["timing", function(n, t, r) {
        var o = e(r, 3)
          , i = o[0]
          , u = o[1]
          , r = o[2]
          , o = F()
          , o = e(nu(o), 3)
          , a = o[0]
          , c = o[1]
          , f = o[2]
          , s = t1(function(n) {
            var t = f("navigation")[0]
              , e = t && t.responseStart;
            return (!e || e <= 0 || e > c()) && (t = void 0),
            {
                ev_type: nF,
                payload: {
                    isBounced: n,
                    timing: a,
                    navigation_timing: t
                }
            }
        }, n, t);
        function l() {
            function n() {
                s(!1)
            }
            var e = u();
            t.push(function() {
                return e[1](n)
            }),
            e[0](n)
        }
        t.push(r[0](function() {
            s(!0)
        })),
        t.push(function() {
            return i[1](l)
        }),
        i[0](l)
    }
    ];
    function ev(n, t) {
        return ~eg.indexOf(n.tagName) || eb < t
    }
    function eh(n) {
        return {
            width: (n = n.getBoundingClientRect()).width,
            height: n.height,
            top: n.top
        }
    }
    function em(n) {
        return n ? document.querySelector(n) : document.body
    }
    es[0];
    var eg = ["SCRIPT", "STYLE", "META", "HEAD"]
      , ey = [nN, nP, nB]
      , eb = 4
      , e_ = [nW, nX, nF, nU];
    function ew(n, t) {
        void 0 === n && (n = 192),
        void 0 === t && (t = 108);
        var e = document.createElement("canvas");
        e.width = n,
        e.height = t;
        var r = e.getContext("2d");
        return r && (r.fillStyle = "#ffffff",
        r.fillRect(0, 0, n, t)),
        e.toDataURL("image/jpeg")
    }
    var ex = function(n, r, o, i) {
        function a(e, o) {
            N || (f = W()) && (N = !0,
            r.forEach(function(n) {
                return n()
            }),
            r.length = 0,
            n({
                ev_type: nz,
                payload: {
                    timestamp: f[0],
                    score: f[1],
                    screenshot: o,
                    error: s,
                    serialized_dom: function n(e, r, o) {
                        if (void 0 === r && (r = 0),
                        void 0 === o && (o = !0),
                        !e || ev(e, r))
                            return "";
                        var i = t(t({}, eh(e)), {
                            id: e.getAttribute("id"),
                            class: e.getAttribute("class")
                        })
                          , u = Object.keys(i).reduce(function(n, t) {
                            return n + (p(i[t]) || i[t] ? " " + t + '="' + i[t] + '"' : "")
                        }, "")
                          , a = e.tagName.toLowerCase()
                          , e = [].reduce.call(e.children, function(t, e) {
                            return t + n(e, r + 1, !1)
                        }, "");
                        return "<" + a + u + (o ? ' innerHeight="' + innerHeight + '"' : "") + ">" + e + "</" + a + ">"
                    }(em(S))
                },
                overrides: {
                    timestamp: e || f[0]
                }
            }))
        }
        function c() {
            v && clearTimeout(v),
            l && clearTimeout(l),
            l = L.setTimeout(function() {
                d = I(function() {
                    (f = W()) && F()
                })
            }, 1e3)
        }
        var f, s, l, d, v, h, m, g = e(o, 5), y = g[0], b = g[1], _ = g[2], w = g[3], x = g[4], E = i.threshold, o = i.screenshot, S = i.rootSelector, g = i.autoDetect, T = i.ssUrl, R = i.quality, j = i.mask, k = i.partialShot, C = i.initDetTime, O = i.runDetTime, L = H(), M = U(), I = L.requestAnimationFrame || u, q = L.cancelAnimationFrame || u, A = e(nu(performance), 2)[1], D = 0, N = !1, P = !o, W = function() {
            var n = em(S);
            if (n)
                return (n = function n(t, e, r, o) {
                    if (void 0 === e && (e = 0),
                    void 0 === r && (r = 0),
                    void 0 === o && (o = 1.5),
                    !t || ev(t, e) || o <= r)
                        return r;
                    var i = function() {
                        if (!e)
                            return 0;
                        var n = eh(t)
                          , r = n.top
                          , n = n.height;
                        return r > innerHeight || n <= 0 ? 0 : 1 / (1 << e - 1)
                    }();
                    return [].reduceRight.call(t.children, function(t, r) {
                        return n(r, e + 1, t, o)
                    }, r + i)
                }(n, 0, 0, E)) < E ? [B(), n] : void 0
        }, F = (h = function() {
            f && !N && (P ? a() : (P = !0,
            function(n) {
                var t = n.cb
                  , e = n.screenshotUrl
                  , r = n.window
                  , o = n.document
                  , i = n.mask
                  , u = n.partialShot
                  , a = n.quality
                  , c = n.rootSelector;
                if (H() && "Promise"in window && Promise && r && o) {
                    if (r.html2canvas)
                        return f(),
                        0;
                    (n = o.createElement("script")).src = e,
                    n.crossOrigin = "anonymous",
                    n.onload = f,
                    n.onerror = function() {
                        t()
                    }
                    ,
                    null !== (e = o.head) && void 0 !== e && e.appendChild(n)
                }
                function f() {
                    (r.requestIdleCallback || function(n) {
                        return r.setTimeout(n, 1)
                    }
                    )(function() {
                        r.html2canvas && r.html2canvas(u && c && o.querySelector(c) || o.body, {
                            scale: 360 / r.innerWidth,
                            mask: i
                        }).then(function(n) {
                            t("data:image" === (n = n.toDataURL("image/jpeg", a)).slice(0, 10) ? n : ew())
                        }).catch(function() {
                            t(ew())
                        })
                    })
                }
            }({
                cb: a.bind(null, B()),
                screenshotUrl: T,
                window: L,
                document: M,
                mask: j,
                partialShot: k,
                quality: R,
                rootSelector: S
            })))
        }
        ,
        function() {
            v && clearTimeout(v),
            m = B(),
            v = L.setTimeout(function() {
                (m < D ? c : h)()
            }, 1e4 < A() ? O : C)
        }
        );
        return r.push(x[0](function() {
            s && a()
        })),
        g && r.push(y[0](function() {
            var n = b();
            r.push(n[0](function() {
                var n = e(K(z(), c), 2)
                  , t = n[0]
                  , o = n[1];
                r.push(function() {
                    clearTimeout(l),
                    clearTimeout(v),
                    q(d),
                    o && o()
                }),
                t(null === (t = U()) || void 0 === t ? void 0 : t.body, {
                    subtree: !0,
                    childList: !0
                }),
                r.push(_()[0](function() {
                    l && c()
                })),
                r.push(w()[0](function() {
                    l && c()
                })),
                c()
            }))
        })),
        [function(n) {
            N || ~e_.indexOf(n.ev_type) || (D = B(),
            s = function(n, t) {
                if (-1 === ey.indexOf(t.ev_type) || t.ev_type === nP && t.payload.response.status < 400 || n && ey.indexOf(n.type) < ey.indexOf(t.ev_type))
                    return n;
                var e = "";
                switch (t.ev_type) {
                case nN:
                    e = t.payload.error.message;
                    break;
                case nP:
                    e = t.payload.request.url;
                    break;
                case nB:
                    e = t.payload.url
                }
                return {
                    type: t.ev_type,
                    message: e,
                    timestamp: B()
                }
            }(s = s && 1e4 < D - s.timestamp ? void 0 : s, n))
        }
        , c]
    }
      , eE = "blankScreen"
      , eS = {
        entries: [],
        observer: void 0
    }
      , eT = "performance"
      , eR = function(n) {
        if (n && c(n) && n.name && v(n.name)) {
            var t = {
                name: n.name,
                type: "event"
            };
            if ("metrics"in n && c(n.metrics)) {
                var e = n.metrics
                  , r = {};
                for (o in e)
                    p(e[o]) && (r[o] = e[o]);
                t.metrics = r
            }
            if ("categories"in n && c(n.categories)) {
                var o, i = n.categories, u = {};
                for (o in i)
                    u[o] = _(i[o]);
                t.categories = u
            }
            return "attached_log"in n && v(n.attached_log) && (t.attached_log = n.attached_log),
            t
        }
    }
      , ej = function(n) {
        if (n && c(n) && n.content && v(n.content)) {
            var t = {
                content: _(n.content),
                type: "log",
                level: "info"
            };
            if ("level"in n && (t.level = n.level),
            "extra"in n && c(n.extra)) {
                var e, r = n.extra, o = {}, i = {};
                for (e in r)
                    p(r[e]) ? o[e] = r[e] : i[e] = _(r[e]);
                t.metrics = o,
                t.categories = i
            }
            return "attached_log"in n && v(n.attached_log) && (t.attached_log = n.attached_log),
            t
        }
    };
    function ek(n) {
        return (null == n ? void 0 : n.effectiveType) || (null == n ? void 0 : n.type) || ""
    }
    function eC(n, t) {
        var e = n.common || {};
        return e.sample_rate = t,
        n.common = e,
        n
    }
    function eO(n, t, e, r, o) {
        var i;
        return n ? (i = o(r, t),
        function() {
            return i
        }
        ) : function() {
            return e(t)
        }
    }
    function eL(n, t, e) {
        var r = t.url
          , o = t.data
          , i = t.success
          , a = void 0 === i ? u : i
          , c = void 0 === (i = t.fail) ? u : i
          , f = void 0 === (i = t.getResponseText) ? u : i
          , t = void 0 !== (t = t.withCredentials) && t;
        (e = new e).withCredentials = t,
        e.open(n, r, !0),
        e.setRequestHeader("Content-Type", "application/json"),
        e.onload = function() {
            null != f && f(this.responseText);
            try {
                var n;
                400 <= this.status ? c(Error(this.responseText || this.statusText)) : this.responseText ? (n = JSON.parse(this.responseText),
                a(n)) : a({})
            } catch (n) {
                c(n)
            }
        }
        ,
        e.onerror = function() {
            c(Error("Network request failed"))
        }
        ,
        e.onabort = function() {
            c(Error("Network request aborted"))
        }
        ,
        e.send(o)
    }
    var eM = function(n) {
        var e = function() {
            var n = function() {
                if (H() && "navigator"in window)
                    return window.navigator
            }();
            if (n)
                return n.connection || n.mozConnection || n.webkitConnection
        }()
          , r = ek(e);
        e && (e.onchange = function() {
            r = ek(e)
        }
        ),
        n.on("report", function(n) {
            return t(t({}, n), {
                extra: t(t({}, n.extra || {}), {
                    network_type: r
                })
            })
        })
    }
      , eI = function(n, t, e, r, o) {
        if (!t)
            return a;
        var i = t.sample_rate
          , u = t.include_users
          , c = t.sample_granularity
          , f = t.rules
          , t = t.r
          , t = void 0 === t ? Math.random() : t;
        if (h(u, n))
            return function(n) {
                return eC(n, 1)
            }
            ;
        var s, l, d = "session" === c, v = eO(d, i, e, t, r), m = (s = t,
        l = {},
        Object.keys(f).forEach(function(n) {
            var t = f[n]
              , o = t.enable
              , u = t.sample_rate
              , t = t.conditional_sample_rules;
            o ? (l[n] = {
                enable: o,
                sample_rate: u,
                effectiveSampleRate: u * i,
                hit: eO(d, u, e, s, r)
            },
            t && (l[n].conditional_hit_rules = t.map(function(n) {
                var t = n.sample_rate
                  , n = n.filter;
                return {
                    sample_rate: t,
                    hit: eO(d, t, e, s, r),
                    effectiveSampleRate: t * i,
                    filter: n
                }
            }))) : l[n] = {
                enable: o,
                hit: function() {
                    return !1
                },
                sample_rate: 0,
                effectiveSampleRate: 0
            }
        }),
        l);
        return function(n) {
            if (!v())
                return d && o[0](),
                !1;
            if (!(n.ev_type in m))
                return eC(n, i);
            if (!m[n.ev_type].enable)
                return d && o[1](n.ev_type),
                !1;
            if (null !== (t = n.common) && void 0 !== t && t.sample_rate)
                return n;
            var t = m[n.ev_type]
              , e = t.conditional_hit_rules;
            if (e) {
                for (var r = 0; r < e.length; r++)
                    if (function n(t, e) {
                        try {
                            return "rule" === e.type ? function(n, t, e, r) {
                                if (void 0 === (n = g(n, t, function(n, t) {
                                    return n[t]
                                })))
                                    return !1;
                                var o, t = "boolean" == typeof n ? "bool" : p(n) ? "number" : "string";
                                return function(n, t, e) {
                                    switch (e) {
                                    case "eq":
                                        return h(t, n);
                                    case "neq":
                                        return !h(t, n);
                                    case "gt":
                                        return n > t[0];
                                    case "gte":
                                        return n >= t[0];
                                    case "lt":
                                        return n < t[0];
                                    case "lte":
                                        return n <= t[0];
                                    case "regex":
                                        return !!n.match(new RegExp(t.join("|")));
                                    case "not_regex":
                                        return !n.match(new RegExp(t.join("|")));
                                    default:
                                        return !1
                                    }
                                }(n, (o = t,
                                r.map(function(n) {
                                    switch (o) {
                                    case "number":
                                        return Number(n);
                                    case "boolean":
                                        return "1" === n;
                                    default:
                                        return String(n)
                                    }
                                })), e)
                            }(t, e.field, e.op, e.values) : "and" === e.type ? e.children.every(function(e) {
                                return n(t, e)
                            }) : e.children.some(function(e) {
                                return n(t, e)
                            })
                        } catch (n) {
                            return V(n),
                            !1
                        }
                    }(n, e[r].filter))
                        return !!e[r].hit() && eC(n, e[r].effectiveSampleRate)
            }
            return t.hit() ? eC(n, t.effectiveSampleRate) : (e && e.length || !d || o[1](n.ev_type),
            !1)
        }
    }
      , eq = "2.8.1"
      , eA = "APM_PLUS_WEB"
      , eD = "/settings/get/webpro"
      , eN = "/monitor_web/collect"
      , eP = [eN, eD, "/monitor_browser/collect"]
      , eB = "session"
      , eH = {
        sample_rate: 1,
        include_users: [],
        sample_granularity: eB,
        rules: {}
    };
    function eU(n, t) {
        return n.plugins.filter(function(n) {
            return n.name === t && n.version === eq
        })[0]
    }
    function eW(n, t, e) {
        (e = void 0 === e ? ni(H()) : e) && e.plugins && (eU(e, n) || e.plugins.push({
            name: n,
            version: eq,
            apply: t
        }))
    }
    var eF = {
        build: function(n) {
            return {
                ev_type: n.ev_type,
                payload: n.payload,
                common: t(t({}, n.extra || {}), n.overrides || {})
            }
        }
    };
    function eX(n) {
        var e, r = n.plugins || {};
        for (e in r)
            r[e] && !c(r[e]) && (r[e] = {});
        return t(t({}, n), {
            plugins: r
        })
    }
    function ez(n) {
        return c(n) && "aid"in n
    }
    function eG(n) {
        return t({}, n)
    }
    function eJ() {
        var n = H()
          , t = U();
        if (n && t)
            return (null === (t = null === (t = null === (t = function() {
                if (!document)
                    return null;
                if (document.currentScript)
                    return document.currentScript;
                try {
                    throw Error()
                } catch (a) {
                    var n = 0
                      , t = /at\s+(.*)\s+\((.*):(\d*):(\d*)\)/i.exec(a.stack)
                      , e = t && t[2] || !1
                      , r = t && t[3] || 0
                      , o = document.location.href.replace(document.location.hash, "")
                      , i = ""
                      , u = document.getElementsByTagName("script");
                    for (e === o && (t = document.documentElement.outerHTML,
                    r = RegExp("(?:[^\\n]+?\\n){0," + (r - 2) + "}[^<]*<script>([\\d\\D]*?)<\\/script>[\\d\\D]*", "i"),
                    i = t.replace(r, "$1").trim()); n < u.length; n++)
                        if ("interactive" === u[n].readyState || u[n].src === e || e === o && u[n].innerHTML && u[n].innerHTML.trim() === i)
                            return u[n];
                    return null
                }
            }()) || void 0 === t ? void 0 : t.getAttribute("src")) || void 0 === t ? void 0 : t.match(/globalName=(.+)$/)) || void 0 === t ? void 0 : t[1]) || eA
    }
    var eY = function(n) {
        var e, r, o, i = n, a = {}, f = u, d = u;
        return {
            getConfig: function() {
                return i
            },
            setConfig: function(n) {
                var u, c, s, l;
                return a = t(t({}, a), n || {}),
                p(),
                e || (e = n,
                i.useLocalConfig ? (o = {},
                f()) : r ? v() : (u = i.transport,
                c = i.domain,
                n = i.aid,
                s = function(n) {
                    r = n,
                    v()
                }
                ,
                u.get({
                    withCredentials: !0,
                    url: (void 0 === l && (l = eD),
                    (c && 0 <= c.indexOf("//") ? "" : "https://") + c + l + "?aid=" + n),
                    success: function(n) {
                        s(n.data || {})
                    },
                    fail: function() {
                        s({
                            sample: {
                                sample_rate: .001
                            }
                        })
                    }
                }))),
                i
            },
            onChange: function(n) {
                d = n
            },
            onReady: function(t) {
                f = function() {
                    var e, r, o, u, a;
                    n.userId !== i.userId && (n.sample.r = Math.random(),
                    p()),
                    a = (u = i).aid,
                    e = u.userId,
                    r = u.deviceId,
                    o = u.sample,
                    u = u.storageExpires,
                    nm(a = "APMPLUS" + a, {
                        userId: e,
                        deviceId: r,
                        r: o.r
                    }, ng(u)),
                    t()
                }
                ,
                o && f()
            }
        };
        function p() {
            var e = t(t(t({}, n), o || {}), a);
            e.plugins = function() {
                for (var n = [], e = 0; e < arguments.length; e++)
                    n[e] = arguments[e];
                for (var r = {}, o = 0; o < n.length; )
                    r = function n(e, r) {
                        var o, i = t({}, e);
                        for (o in r)
                            Object.prototype.hasOwnProperty.call(r, o) && void 0 !== r[o] && (c(r[o]) && s(r[o]) ? i[o] = n(c(e[o]) ? e[o] : {}, r[o]) : l(r[o]) && l(e[o]) ? i[o] = function t(e, r) {
                                return e = l(e) ? e : [],
                                r = l(r) ? r : [],
                                Array.prototype.concat.call(e, r).map(function(e) {
                                    return e instanceof RegExp ? e : c(e) && s(e) ? n({}, e) : l(e) ? t([], e) : e
                                })
                            }(e[o], r[o]) : i[o] = r[o]);
                        return i
                    }(r, n[o++]);
                return r
            }(n.plugins, (null == o ? void 0 : o.plugins) || {}, a.plugins || {}),
            e.sample = e$(e$(n.sample, null == o ? void 0 : o.sample), a.sample),
            i = e,
            d()
        }
        function v() {
            o = function(n) {
                if (!n)
                    return {};
                var t = n.sample
                  , e = n.timestamp
                  , r = n.status
                  , o = n.apdex;
                if (!t)
                    return {};
                var i = t.sample_rate
                  , u = t.sample_granularity
                  , n = t.include_users
                  , t = t.rules;
                return {
                    sample: {
                        include_users: n,
                        sample_rate: r && 4 === r ? 0 : i,
                        sample_granularity: void 0 === u ? eB : u,
                        rules: (void 0 === t ? [] : t).reduce(function(n, t) {
                            var e = t.name
                              , r = t.enable
                              , o = t.sample_rate
                              , t = t.conditional_sample_rules;
                            return n[e] = {
                                enable: r,
                                sample_rate: o,
                                conditional_sample_rules: t
                            },
                            n
                        }, {})
                    },
                    apdex: o,
                    serverTimestamp: e
                }
            }(r),
            p(),
            f()
        }
    };
    function e$(n, o) {
        if (!n || !o)
            return n || o;
        var i = t(t({}, n), o);
        return i.include_users = r(r([], e(n.include_users || []), !1), e(o.include_users || []), !1),
        i.rules = r(r([], e(Object.keys(n.rules || {})), !1), e(Object.keys(o.rules || {})), !1).reduce(function(i, u) {
            var a;
            return u in i || (u in (n.rules || {}) && u in (o.rules || {}) ? (i[u] = t(t({}, n.rules[u]), o.rules[u]),
            i[u].conditional_sample_rules = r(r([], e(n.rules[u].conditional_sample_rules || []), !1), e(o.rules[u].conditional_sample_rules || []), !1)) : i[u] = (null === (a = n.rules) || void 0 === a ? void 0 : a[u]) || (null === (a = o.rules) || void 0 === a ? void 0 : a[u])),
            i
        }, {}),
        i
    }
    var eV = function(n) {
        n.on("report", function(e) {
            var r, o;
            return r = e,
            o = void 0 === (o = (e = (o = n.config()) || {}).pid) ? "" : o,
            e = void 0 === (e = e.viewId) ? "" : e,
            e = {
                url: $(),
                timestamp: Date.now(),
                pid: o,
                view_id: e
            },
            t(t({}, r), {
                extra: t(t({}, e), r.extra || {})
            })
        })
    }
      , eK = {
        sri: "reportSri",
        st: "reportResourceError",
        err: "captureException",
        reject: "captureException"
    }
      , eQ = function(n, t) {
        return "err" === t ? !1 !== g(n, "plugins." + tw + ".onerror", function(n, t) {
            return n[t]
        }) : "reject" !== t || !1 !== g(n, "plugins." + tw + ".onunhandledrejection", function(n, t) {
            return n[t]
        })
    }
      , eZ = function(n) {
        var t, e = !1;
        n.on("init", function() {
            t = (new Date).getTime(),
            n.on("config", function() {
                var r, o = null === (r = n.config()) || void 0 === r ? void 0 : r.serverTimestamp;
                isNaN(o) || 0 >= Number(o) || e || (e = !0,
                (r = (new Date).getTime()) - t < 700 && o && !isNaN(r = o - (r + t) / 2) && (0 < r || r < -6e5) && n.set({
                    offset: r
                }))
            })
        })
    }
      , e0 = function(n) {
        n.on("beforeBuild", function(e) {
            var r, o;
            return r = e,
            o = n.config(),
            (e = {}).aid = o.aid,
            e.user_id = o.userId,
            t(t({}, r), {
                extra: t(t({}, e), r.extra || {})
            })
        })
    }
      , e1 = function(n) {
        n.on("start", function() {
            var t, e = n.config(), r = e.deviceId, o = e.sessionId, i = e.release, u = e.env, a = e.offset, f = e.aid, e = e.token, f = {
                did: r,
                sid: o,
                release: i,
                env: u,
                sname: eA,
                sversion: eq,
                soffset: a || 0,
                biz_id: f,
                x_auth_token: e
            }, e = n.getSender();
            e.setEndpoint(e.getEndpoint() + (c(t = f) ? Object.keys(t).reduce(function(n, e) {
                return n + ("&" + e + "=") + t[e]
            }, "").replace("&", "?") : ""))
        })
    }
      , e2 = function(n) {
        var e, r, o, i, a = ng(n.storageExpires), n = (e = n.aid,
        r = a,
        void 0 === e && (e = 0),
        o = {
            userId: L(),
            deviceId: L(),
            r: Math.random()
        },
        r <= 0 ? o : (function(n, t) {
            try {
                var e = localStorage.getItem(n);
                if (!e || !np() || "{" !== e[0])
                    return;
                nm(n, JSON.parse(e), t)
            } catch (n) {}
        }(e = "APMPLUS" + e, r),
        function(n) {
            try {
                var t = localStorage.getItem(n)
                  , e = t
                  , r = e = t && "string" == typeof t ? JSON.parse(np() ? decodeURI(atob(t)) : t) : e
                  , o = r.expires
                  , i = function(n, t) {
                    var e = {};
                    for (o in n)
                        Object.prototype.hasOwnProperty.call(n, o) && 0 > t.indexOf(o) && (e[o] = n[o]);
                    if (null != n && "function" == typeof Object.getOwnPropertySymbols)
                        for (var r = 0, o = Object.getOwnPropertySymbols(n); r < o.length; r++)
                            0 > t.indexOf(o[r]) && Object.prototype.propertyIsEnumerable.call(n, o[r]) && (e[o[r]] = n[o[r]]);
                    return e
                }(r, ["expires"]);
                return o >= B() ? i : void 0
            } catch (n) {
                return
            }
        }(e) || o));
        return {
            aid: 0,
            pid: "",
            token: "",
            viewId: tA("_"),
            userId: n.userId,
            deviceId: n.deviceId,
            sessionId: L(),
            storageExpires: a,
            domain: "apmplus.volces.com",
            plugins: {
                ajax: {
                    ignoreUrls: eP
                },
                fetch: {
                    ignoreUrls: eP
                },
                breadcrumb: {},
                pageview: {},
                jsError: {},
                resource: {},
                resourceError: {},
                performance: {},
                tti: {},
                fmp: {},
                blankScreen: !1
            },
            release: "",
            env: "production",
            sample: t(t({}, eH), {
                r: n.r
            }),
            transport: (i = X()) ? {
                useBeacon: !0,
                get: function(n) {
                    eL("GET", n, i)
                },
                post: function(n) {
                    eL("POST", n, i)
                }
            } : {
                get: u,
                post: u
            }
        }
    }
      , e3 = ((e6 = {})[tW] = function(n) {
        n.on("init", function() {
            var r, o, i, a, c, f, s, l, d, p, v, h = null === (i = n.config()) || void 0 === i ? void 0 : i.plugins[tW];
            (v = nh(r = h, tF)) && W() && (o = v.routeMode,
            c = v.apdex,
            l = n.report.bind(n),
            s = u,
            c && (i = [],
            r = (h = e(tU(n.report.bind(n), i, [N(n, tk), N(n, tO)], v), 4))[0],
            a = h[1],
            c = h[2],
            f = h[3],
            l = c,
            s = r,
            n.on("send", a),
            i.push(function() {
                return n.off("send", a)
            }),
            n.on("start", function() {
                f(n.config().apdex)
            }),
            q(n, tW, nD, i)),
            d = e(tH(l, l = [], tD(o) ? [] : [n.initSubject(tI), n.initSubject(tq)], t(t({}, v), {
                initPid: null === (v = n.config()) || void 0 === v ? void 0 : v.pid,
                onPidUpdate: function(t) {
                    var e = tA(t);
                    s(t, e),
                    n.set({
                        pid: t,
                        viewId: e,
                        actionId: void 0
                    })
                }
            })), 1)[0],
            P(n, [nr, no(n)], -1),
            p = function() {
                d(n.config().pid)
            }
            ,
            n.on("config", p),
            l.push(function() {
                return n.off("config", p)
            }),
            q(n, tW, nA, l),
            n.provide("sendPageview", d))
        })
    }
    ,
    e6[n1] = function(n) {
        n.on("init", function() {
            var r, o, i, a, c, f, s, l, d, p = n0(n, n1, n2);
            p && (r = [],
            (a = t(t({}, p), {
                setContextAtReq: function() {
                    return nn(n, !0)
                },
                setTraceHeader: n_(p.trace, "app_id=" + (null === (o = n.config()) || void 0 === o ? void 0 : o.aid) + ",origin=web")
            })).autoWrap && (p = r,
            o = [N(n, [nx, nR(XMLHttpRequest && XMLHttpRequest.prototype)]), function() {
                return N(n, nq)
            }
            ],
            i = a,
            o = (a = e(o, 2))[0],
            c = a[1],
            f = i.setTraceHeader,
            s = i.ignoreUrls,
            l = i.setContextAtReq,
            d = i.extractUrl,
            p.push(o[0](function(n) {
                var t = e(n, 4);
                t[0],
                n = t[1],
                t[2];
                var r = t[3];
                if (!n)
                    return u;
                var o = J(n);
                if (b(s, o))
                    return u;
                f && f(o, function(n, t) {
                    return r.setRequestHeader(n, t)
                });
                var a = l()
                  , p = void 0
                  , v = c()[0](function(n) {
                    o !== n.name || p || (p = n)
                });
                return function(n) {
                    var t = nZ(n, i);
                    setTimeout(function() {
                        p && (t.response.timing = p),
                        nQ(t, d),
                        a && a({
                            ev_type: nP,
                            payload: t
                        }),
                        v()
                    }, 100)
                }
            }))),
            q(n, n1, nP, r))
        })
    }
    ,
    e6[ta] = function(n) {
        n.on("init", function() {
            var r, o, i, a, c, f, s, l, d, p, v, h = n0(n, ta, tc);
            h && (r = [],
            (a = t(t({}, h), {
                setContextAtReq: function() {
                    return nn(n, !0)
                },
                setTraceHeader: n_(h.trace, "app_id=" + (null === (o = n.config()) || void 0 === o ? void 0 : o.aid) + ",origin=web")
            })).autoWrap && (h = r,
            o = [N(n, nj), function() {
                return N(n, nq)
            }
            ],
            i = a,
            o = (a = e(o, 2))[0],
            c = a[1],
            f = i.setTraceHeader,
            s = i.ignoreUrls,
            l = i.setContextAtReq,
            d = i.extractUrl,
            p = window.Headers,
            (v = window.Request) && p && h.push(o[0](function(n) {
                var n = e(n, 2)
                  , t = n[0]
                  , r = n[1]
                  , o = J(t instanceof v ? t.url : t);
                if (!to(o) || b(s, o))
                    return u;
                f && f(o, function(n, e) {
                    return ti(n, e, t, r, v, p)
                });
                var a = l()
                  , h = B()
                  , m = void 0
                  , g = c()[0](function(n) {
                    o !== n.name || m || (m = n)
                });
                return function(n) {
                    var e = tu(t, r, n, v, p, i, h)
                      , o = nK(function(n) {
                        m && (n.response.timing = m),
                        nQ(n, d),
                        a && a({
                            ev_type: nP,
                            payload: n
                        }),
                        g()
                    });
                    setTimeout(function() {
                        o(e)
                    }, 1e3)
                }
            }))),
            q(n, ta, nP, r))
        })
    }
    ,
    e6.tti = function(n) {
        n.on("init", function() {
            var t;
            n0(n, "tti", {}) && (t = [],
            ee(nn(n), t, [N(n, [nx, nR(XMLHttpRequest && XMLHttpRequest.prototype)]), N(n, nj), N(n, nI), N(n, nq), P(n, [nt, ne(n)])], n.pp),
            q(n, "tti", nW, t))
        })
    }
    ,
    e6.fmp = function(n) {
        n.on("init", function() {
            var t, e = n0(n, "fmp", ei);
            e && (t = [],
            "SSR" === (e = void 0 === e ? ei : e).renderType ? t9(t7, "fmp", nn(n), t, [N(n, tM), function() {
                return N(n, tk)
            }
            , function() {
                return N(n, tO)
            }
            ]) : eo(nn(n), t, [N(n, tC), P(n, [nt, ne(n)])]),
            q(n, "fmp", nW, t))
        })
    }
    ,
    e6[n7] = function(n) {
        n.on("init", function() {
            var t, r, o, i, u = null === (i = n.config()) || void 0 === i ? void 0 : i.plugins[n7];
            (i = nh(t = u, n9)) && (i = (t = e(n8(u = [], [N(n, n5), N(n, n6)], i), 2))[0],
            r = t[1],
            n.on("report", o = function(n) {
                return n.ev_type === nP && r({
                    type: nP,
                    category: n.payload.api,
                    message: "",
                    data: {
                        method: n.payload.request.method,
                        url: n.payload.request.url,
                        status_code: String(n.payload.response.status)
                    },
                    timestamp: n.payload.request.timestamp
                }),
                n
            }
            ),
            u.push(function() {
                n.off("report", o)
            }),
            q(n, n7, nN, u),
            n.provide("getBreadcrumbs", i),
            n.provide("addBreadcrumb", r))
        })
    }
    ,
    e6[tw] = function(n) {
        n.on("init", function() {
            var t, e, r = null === (r = n.config()) || void 0 === r ? void 0 : r.plugins[tw];
            t = r,
            window.removeEventListener("error", n.pcErr, !0),
            window.removeEventListener("unhandledrejection", n.pcRej, !0),
            (e = nh(t, tx)) && (e = t_(function(t) {
                n.getBreadcrumbs && (t.payload.breadcrumbs = n.getBreadcrumbs()),
                n.report(t)
            }, t = [], [N(n, ty), N(n, tb), function() {
                return N(n, tg)
            }
            ], e),
            q(n, tw, nN, t),
            n.provide("captureException", e))
        })
    }
    ,
    e6[eT] = function(n) {
        n.on("init", function() {
            var r, o, i, u = n.pp || eS;
            null !== (h = u.observer) && void 0 !== h && h.disconnect();
            var a, c, f, s, l, d, p, v, h, m, g = n0(n, eT, {});
            g && (a = function() {
                return N(n, tM)
            }
            ,
            c = function() {
                return N(n, tk)
            }
            ,
            f = function() {
                return N(n, tO)
            }
            ,
            s = N(n, tC),
            l = N(n, nI),
            d = void 0,
            P(n, [nr, no(n)], -1)[0](function(n) {
                d = n
            })(),
            p = function(e) {
                e = e.ev_type === nW && (e.payload.name === ec[0] || e.payload.name === es[0]) || e.ev_type === nX ? e : t(t({}, e), {
                    overrides: d
                }),
                n.report(e)
            }
            ,
            v = function() {
                return P(n, [nt, ne(n)])
            }
            ,
            [en, et, ea, es, ec].forEach(function(t) {
                !1 !== g[t[0]] && (t[1](p, t = [], [a(), c, f, v]),
                q(n, eT, nW, t))
            }),
            [ed, ep].forEach(function(t) {
                var e;
                !1 !== g[t[0]] && (t[1](p, e = [], [s, a, f(), l]),
                q(n, eT, t = t[0] === el ? nX : "timing" === t[0] ? nF : nW, e))
            }),
            h = (m = e((r = n.report.bind(n),
            o = 0,
            i = t0("spa_load", 0),
            [function() {
                o = B()
            }
            , function() {
                i.value = B() - o,
                r && r(t2(i)),
                o = 0
            }
            ]), 2))[0],
            m = m[1],
            n.provide("performanceInit", h),
            n.provide("performanceSend", m),
            u.entries.length = 0,
            n.provide("sendCustomPerfMetric", function(e) {
                e = t(t(t({}, tZ), e), {
                    isCustom: !0
                }),
                n.report(t2(e))
            }))
        })
    }
    ,
    e6[tV] = function(n) {
        n.on("init", function() {
            var t, r = n0(n, tV, tK);
            r && (t = [],
            r = function(n, t, r, o) {
                var i = e(r, 1)[0]
                  , u = H();
                if (u) {
                    var a = o.ignoreUrls
                      , r = o.includeUrls
                      , c = o.dedupe
                      , f = o.gatherPath
                      , s = y(r)
                      , l = y(a)
                      , d = e(nu(F()), 5)[4]
                      , p = void 0
                      , v = function(t) {
                        var e = location && location.href;
                        e && t.url === e || s && !s.test(t.url) || l && l.test(t.url) || t.url && (c && t.url === p || (p = t.url,
                        (t = t$(t, d)) && n({
                            ev_type: nB,
                            payload: t
                        })))
                    };
                    return t.push(i[0](function(n) {
                        !(n = n || u.event) || (n = tY(n, f)) && v(n)
                    })),
                    v
                }
            }(n.report.bind(n), t, [N(n, ty)], r),
            q(n, tV, nB, t),
            r && n.provide("reportResourceError", r))
        })
    }
    ,
    e6[tG] = function(n) {
        n.on("init", function() {
            var t, e = null === (t = n.config()) || void 0 === t ? void 0 : t.plugins[tG];
            (e = nh(t = e, tJ)) && (t = [],
            tz(n.report.bind(n), t, [N(n, tC), function() {
                return N(n, nq)
            }
            ], e),
            q(n, tG, nH, t))
        })
    }
    ,
    e6[eE] = function(n, t) {
        n.on("init", function() {
            var r, o, i, u = {
                autoDetect: !0,
                threshold: 1.5,
                screenshot: !0,
                ssUrl: "https://apm.volccdn.com/mars-web/apmplus/web/html2canvas.min.js",
                mask: !1,
                partialShot: !0,
                quality: .1,
                initDetTime: 8e3,
                runDetTime: 4e3
            }, a = t ? nh(t, u) : n0(n, eE, u);
            a && (r = a,
            u = U(),
            a = H(),
            u && a && (a = [],
            o = (r = e(ex(n.report.bind(n), a, [N(n, tM), function() {
                return N(n, tL)
            }
            , function() {
                return N(n, nI)
            }
            , function() {
                return N(n, nq)
            }
            , N(n, tO)], r), 2))[0],
            r = r[1],
            n.on("report", i = function(n) {
                return o(n),
                n
            }
            ),
            a.push(function() {
                n.off("report", i)
            }),
            q(n, eE, nz, a),
            n.provide("detectBlankScreen", r)))
        })
    }
    ,
    e6)
      , e4 = function n(a) {
        var f, s, l, d, p, v, g, y, b, _, w, S, T, R, k, L, M = (y = (T = void 0 === (b = a = void 0 === a ? {} : a) ? {} : b).createSender,
        A(_ = function(n) {
            var t, o, u = n.builder, a = n.createSender, f = n.createDefaultConfig, s = n.createConfigManager, l = n.userConfigNormalizer, d = n.initConfigNormalizer, p = n.validateInitConfig, v = {};
            i.forEach(function(n) {
                return v[n] = []
            });
            var g = !1
              , y = !1
              , b = !1
              , _ = []
              , w = []
              , S = function() {
                function n(n) {
                    n.length && n.forEach(function(n) {
                        try {
                            n()
                        } catch (n) {}
                    }),
                    n.length = 0
                }
                function t(t) {
                    r[t] && r[t].forEach(function(t) {
                        n(t[1])
                    }),
                    r[t] = void 0
                }
                var e = !1
                  , r = {};
                return {
                    set: function(t, o, i) {
                        r[t] ? r[t].push([o, i]) : r[t] = [[o, i]],
                        e && n(i)
                    },
                    has: function(n) {
                        return !!r[n]
                    },
                    remove: t,
                    removeByEvType: function(t) {
                        Object.keys(r).forEach(function(e) {
                            r[e] && r[e].forEach(function(e) {
                                e[0] === t && n(e[1])
                            })
                        })
                    },
                    clear: function() {
                        e = !0,
                        Object.keys(r).forEach(function(n) {
                            t(n)
                        })
                    }
                }
            }()
              , T = {
                getBuilder: function() {
                    return u
                },
                getSender: function() {
                    return t
                },
                getPreStartQueue: function() {
                    return _
                },
                init: function(n) {
                    if (g)
                        x("already inited");
                    else {
                        if (!(n && c(n) && p(n)))
                            throw Error("invalid InitConfig, init failed");
                        var e = f(n);
                        if (!e)
                            throw Error("defaultConfig missing");
                        if (n = d(n),
                        (o = s(e)).setConfig(n),
                        o.onChange(function() {
                            R("config")
                        }),
                        !(t = a(o.getConfig())))
                            throw Error("sender missing");
                        R("init", g = !0)
                    }
                },
                set: function(n) {
                    g && n && c(n) && (R("beforeConfig", !1, n),
                    null != o && o.setConfig(n))
                },
                config: function(n) {
                    if (g)
                        return n && c(n) && (R("beforeConfig", !1, n),
                        null != o && o.setConfig(l(n))),
                        null == o ? void 0 : o.getConfig()
                },
                provide: function(n, t) {
                    h(w, n) ? x("cannot provide " + n + ", reserved") : (T[n] = t,
                    R("provide", !1, n))
                },
                start: function() {
                    var n = this;
                    g && (y || null != o && o.onReady(function() {
                        R("start", y = !0),
                        _.forEach(function(t) {
                            return n.build(t)
                        }),
                        _.length = 0
                    }))
                },
                report: function(n) {
                    n && (!(n = E(v.beforeReport)(n)) || (n = E(v.report)(n)) && (y ? this.build(n) : _.push(n)))
                },
                build: function(n) {
                    !y || (n = E(v.beforeBuild)(n)) && (!(n = u.build(n)) || (n = E(v.build)(n)) && this.send(n))
                },
                send: function(n) {
                    !y || (n = E(v.beforeSend)(n)) && (t.send(n),
                    R("send", !1, n))
                },
                destroy: function() {
                    S.clear(),
                    b = !0,
                    R("beforeDestroy", (_.length = 0,
                    !0))
                },
                on: function(n, t) {
                    if ("init" === n && g || "start" === n && y || "beforeDestroy" === n && b)
                        try {
                            t()
                        } catch (n) {}
                    else
                        v[n] && v[n].push(t)
                },
                off: function(n, t) {
                    v[n] && (v[n] = m(v[n], t))
                },
                destroyAgent: S
            }
              , w = Object.keys(T);
            return T;
            function R(n, t) {
                void 0 === t && (t = !1);
                for (var o = [], i = 2; i < arguments.length; i++)
                    o[i - 2] = arguments[i];
                v[n].forEach(function(n) {
                    try {
                        n.apply(void 0, r([], e(o), !1))
                    } catch (n) {}
                }),
                t && (v[n].length = 0)
            }
        }({
            validateInitConfig: ez,
            initConfigNormalizer: eX,
            userConfigNormalizer: eG,
            createSender: void 0 === y ? function(n) {
                var t, r;
                return function(n) {
                    var t, r, i, a, c, f, s, l, d, p, v, h = (c = (i = n).transport,
                    f = n.endpoint,
                    l = void 0 === (s = n.size) ? 10 : s,
                    d = void 0 === (i = n.wait) ? 1e3 : i,
                    p = [],
                    v = 0,
                    {
                        getSize: function() {
                            return l
                        },
                        getWait: function() {
                            return d
                        },
                        setSize: function(n) {
                            l = n
                        },
                        setWait: function(n) {
                            d = n
                        },
                        getEndpoint: function() {
                            return f
                        },
                        setEndpoint: function(n) {
                            f = n
                        },
                        send: function(n) {
                            p.push(n),
                            p.length >= l && m.call(this),
                            clearTimeout(v),
                            v = setTimeout(m.bind(this), d)
                        },
                        flush: function() {
                            clearTimeout(v),
                            m.call(this)
                        },
                        getBatchData: function() {
                            return p.length ? o(p) : ""
                        },
                        clear: function() {
                            clearTimeout(v),
                            p = []
                        },
                        fail: function(n) {
                            a = n
                        }
                    });
                    function m() {
                        var n;
                        p.length && (n = this.getBatchData(),
                        c.post({
                            url: f,
                            data: n,
                            fail: function(t) {
                                a && a(t, n)
                            }
                        }),
                        p = [])
                    }
                    var g = h.send;
                    return (r = H()) && (t = e(nv(function() {
                        var t, e, r, i, a, c, f;
                        n.transport.useBeacon ? (t = (r = H()) && r.navigator.sendBeacon ? {
                            get: function() {},
                            post: function(n, t) {
                                r.navigator.sendBeacon(n, t)
                            }
                        } : {
                            get: u,
                            post: u
                        },
                        (e = h.getBatchData()) && (t.post(h.getEndpoint(), e),
                        h.clear()),
                        h.send = function(n) {
                            t.post(h.getEndpoint(), o([n]))
                        }
                        ,
                        i = function() {
                            h.send = g
                        }
                        ,
                        c = U(),
                        f = H(),
                        c && f && (a = u,
                        a = nd(c, "visibilitychange", function() {
                            "visible" === c.visibilityState && (i(),
                            a())
                        }, !0))) : h.flush()
                    }), 1)[0],
                    ["unload", "beforeunload", "pagehide"].forEach(function(n) {
                        nl(r, n, t, !1)
                    })),
                    h
                }({
                    size: 20,
                    endpoint: (t = n.domain,
                    void 0 === r && (r = eN),
                    (t && 0 <= t.indexOf("//") ? "" : "https://") + t + r),
                    transport: n.transport
                })
            }
            : y,
            builder: void 0 === (b = T.builder) ? eF : b,
            createDefaultConfig: void 0 === (T = T.createDefaultConfig) ? e2 : T,
            createConfigManager: eY
        })),
        w = (T = (T = ni(H())) && T.subject) || {},
        S = {},
        _.provide("setFilter", function(n, t) {
            S[n] || (S[n] = []),
            S[n].push(t)
        }),
        _.provide("initSubject", function(n) {
            var t, r, o, i = e(n, 2), a = i[0], n = i[1], i = a.split("_")[0], i = !!i && S[i];
            return w[a] || (w[a] = I(n, function() {
                w[a] = void 0
            })),
            i ? P(_, [a, (t = w[a],
            r = i,
            o = e(t, 1)[0],
            function(n, t) {
                var e = o(function(t) {
                    return !function(n) {
                        for (var t = !0, e = 0; e < r.length && t; e++)
                            try {
                                t = r[e](n)
                            } catch (n) {
                                j(n)
                            }
                        return t
                    }(t) ? u : n(t)
                });
                t(function() {
                    e()
                })
            }
            )]) : w[a]
        }),
        _.provide("getSubject", function(n) {
            return w[n]
        }),
        _.provide("privateSubject", {}),
        eZ(_),
        e0(_),
        eV(_),
        eM(_),
        e1(_),
        function(n, t) {
            n.on("init", function() {
                function e(e) {
                    e.forEach(function(e) {
                        var o = e.name;
                        h(r, o) || (r.push(o),
                        e.setup(n),
                        t && t(o, e.setup),
                        n.destroyAgent.set(o, o, [function() {
                            r = m(r, o),
                            e.tearDown && e.tearDown()
                        }
                        ]))
                    })
                }
                var r = [];
                n.provide("applyIntegrations", e);
                var o = n.config();
                o && o.integrations && e(o.integrations)
            })
        }(T = D(_, na, function(n, t, o) {
            return nc(n, t)(function() {
                var n = e(o)
                  , t = n[0]
                  , n = n.slice(1);
                _[t].apply(_, r([], e(n), !1))
            })
        }), eW),
        T);
        return M.on("start", function() {
            var n = M.config()
              , t = n.userId
              , n = n.sample
              , n = eI(t, n, C, O, [function() {
                M.destroy()
            }
            , function(n) {
                M.destroyAgent.removeByEvType(n)
            }
            ]);
            M.on("build", n)
        }),
        k = Object.keys(R = void 0 === R ? eK : R).reduce(function(n, t) {
            return n[t] = [],
            n
        }, {}),
        a = Object.keys(f = R).reduce(function(n, t) {
            return n[f[t]] ? n[f[t]].push(t) : n[f[t]] = [t],
            n
        }, {}),
        s = M,
        l = k,
        d = R,
        L = function(n, e, r, o) {
            void 0 === r && (r = B()),
            void 0 === o && (o = location.href),
            o = t(t({}, na(s)), {
                url: o,
                timestamp: r
            }),
            l[n] && (s[d[n]] ? nc(s, o)(function() {
                s[d[n]](e)
            }) : null !== (r = l[n]) && void 0 !== r && r.push([e, o]))
        }
        ,
        null !== (R = M.p) && void 0 !== R && R.a && "observe"in M.p.a && M.p.a.observe(function(n) {
            var t = e(n, 5);
            t[0];
            var r = t[1]
              , o = t[2]
              , i = t[3]
              , n = t[4]
              , t = M.config();
            eQ(t, r) && L(r, o, i, n)
        }),
        M.on("init", function() {
            var n, t = M.config();
            null !== (n = M.p) && void 0 !== n && n.a.forEach(function(n) {
                var r = e(n, 5);
                r[0];
                var o = r[1]
                  , i = r[2]
                  , n = r[3]
                  , r = r[4];
                eQ(t, o) && L(o, i, n, r)
            }),
            M.p && M.p.a && (M.p.a.length = 0),
            M.provide("precollect", function(n, e, r, o) {
                void 0 === r && (r = B()),
                void 0 === o && (o = location.href),
                eQ(t, n) && L(n, e, r, o)
            })
        }),
        M.on("provide", (p = M,
        v = k,
        g = a,
        function(n) {
            n in g && g[n].forEach(function(t) {
                var r;
                null !== (r = v[t]) && void 0 !== r && r.forEach(function(t) {
                    var t = e(t, 2)
                      , r = t[0]
                      , t = t[1];
                    nc(p, t)(function() {
                        p[n](r)
                    })
                }),
                v[t] = null
            })
        }
        )),
        M.provide("sendEvent", function(n) {
            (n = eR(n)) && M.report({
                ev_type: nU,
                payload: n,
                extra: {
                    timestamp: B()
                }
            })
        }),
        M.provide("sendLog", function(n) {
            (n = ej(n)) && M.report({
                ev_type: nU,
                payload: n,
                extra: {
                    timestamp: B()
                }
            })
        }),
        Object.keys(e3).forEach(function(n) {
            eW(n, e3[n]),
            e3[n](M)
        }),
        function(n) {
            n.provide("reloadPlugin", function(e, r) {
                var o;
                n.destroyAgent.has(e) && n.destroyAgent.remove(e),
                void 0 !== r && n.set({
                    plugins: t(t({}, n.config().plugins), ((o = {})[e] = r,
                    o))
                }),
                n.config().plugins[e] && function(n, t, e) {
                    if (void 0 === e && (e = ni(H())),
                    e) {
                        if (e = eU(e, t))
                            try {
                                if (n.destroyAgent.has(t))
                                    return;
                                e.apply(n)
                            } catch (n) {
                                x("[loader].applyPlugin failed", t, n)
                            }
                        else
                            x("[loader].applyPlugin not found", t)
                    }
                }(n, e)
            })
        }(M),
        M.provide("create", n),
        M
    }()
      , e5 = function() {
        var n = H()
          , t = eJ();
        if (n && t)
            return n[t]
    }();
    e5 && ["p", "pp", "pcErr", "pcRej"].forEach(function(n) {
        e4.provide(n, e5[n])
    });
    var e6, e8, e7, e9, rn = H(), rt = eJ();
    rn && rt && (e6 = (null == (e6 = rn[rt]) ? void 0 : e6.q) || [],
    rn[rt] = e4,
    e6.forEach(function(n) {
        var o;
        o = n,
        n = t(t({}, na(e4)), {
            url: o.pop(),
            timestamp: o.pop()
        }),
        nc(e4, n)(function() {
            e4.apply(void 0, r([], e(o), !1))
        })
    }),
    e6.length = 0,
    e4.p && ("observe"in e4.p.a && console.warn("global precollect queue already updated"),
    e4.p.a = (e7 = e4.p.a,
    e9 = [],
    e7.observe = function(n) {
        e9.push(n)
    }
    ,
    e7.push = function() {
        for (var n, t = [], o = 0; o < arguments.length; o++)
            t[o] = arguments[o];
        return t.forEach(function(n) {
            e9.forEach(function(t) {
                return t(n)
            })
        }),
        (n = [].push).call.apply(n, r([e7], e(t), !1))
    }
    ,
    e7),
    (e8 = e4.precollect) && e4.provide("precollect", function() {
        for (var n = [], t = 0; t < arguments.length; t++)
            n[t] = arguments[t];
        return e4.p.a.push(r(["precollect"], e(n), !1)),
        e8.apply(void 0, r([], e(n), !1))
    })))
}();
