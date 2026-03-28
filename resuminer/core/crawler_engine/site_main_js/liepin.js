var e, t;
e = this,
t = function(r) {
    "use strict";
    function n(r, n) {
        return null != n && "undefined" != typeof Symbol && n[Symbol.hasInstance] ? !!n[Symbol.hasInstance](r) : r instanceof n
    }
    function o(r) {
        return r && "undefined" != typeof Symbol && r.constructor === Symbol ? "symbol" : typeof r
    }
    Object.defineProperty(r, "__esModule", {
        value: !0
    }),
    Object.defineProperty(r, "default", {
        enumerable: !0,
        get: function() {
            return ow
        }
    });
    var i = Object.getOwnPropertyNames
      , u = function(r, n) {
        return function() {
            return n || (0,
            r[i(r)[0]])((n = {
                exports: {}
            }).exports, n),
            n.exports
        }
    }
      , a = u({
        "node_modules/core-js-pure/internals/global-this.js": function(r, n) {
            var o = function(r) {
                return r && r.Math === Math && r
            };
            n.exports = o("object" == typeof globalThis && globalThis) || o("object" == typeof window && window) || o("object" == typeof self && self) || o("object" == typeof global && global) || o("object" == typeof r && r) || function() {
                return this
            }() || Function("return this")()
        }
    })
      , c = u({
        "node_modules/core-js-pure/internals/fails.js": function(r, n) {
            n.exports = function(r) {
                try {
                    return !!r()
                } catch (r) {
                    return !0
                }
            }
        }
    })
      , s = u({
        "node_modules/core-js-pure/internals/function-bind-native.js": function(r, n) {
            n.exports = !c()(function() {
                var r = (function() {}
                ).bind();
                return "function" != typeof r || r.hasOwnProperty("prototype")
            })
        }
    })
      , l = u({
        "node_modules/core-js-pure/internals/function-apply.js": function(r, n) {
            var o = s()
              , i = Function.prototype
              , u = i.apply
              , a = i.call;
            n.exports = "object" == typeof Reflect && Reflect.apply || (o ? a.bind(u) : function() {
                return a.apply(u, arguments)
            }
            )
        }
    })
      , f = u({
        "node_modules/core-js-pure/internals/function-uncurry-this.js": function(r, n) {
            var o = s()
              , i = Function.prototype
              , u = i.call
              , a = o && i.bind.bind(u, u);
            n.exports = o ? a : function(r) {
                return function() {
                    return u.apply(r, arguments)
                }
            }
        }
    })
      , d = u({
        "node_modules/core-js-pure/internals/classof-raw.js": function(r, n) {
            var o = f()
              , i = o({}.toString)
              , u = o("".slice);
            n.exports = function(r) {
                return u(i(r), 8, -1)
            }
        }
    })
      , p = u({
        "node_modules/core-js-pure/internals/function-uncurry-this-clause.js": function(r, n) {
            var o = d()
              , i = f();
            n.exports = function(r) {
                if ("Function" === o(r))
                    return i(r)
            }
        }
    })
      , v = u({
        "node_modules/core-js-pure/internals/is-callable.js": function(r, n) {
            var o = "object" == typeof document && document.all;
            n.exports = void 0 === o && void 0 !== o ? function(r) {
                return "function" == typeof r || r === o
            }
            : function(r) {
                return "function" == typeof r
            }
        }
    })
      , h = u({
        "node_modules/core-js-pure/internals/descriptors.js": function(r, n) {
            n.exports = !c()(function() {
                return 7 !== Object.defineProperty({}, 1, {
                    get: function() {
                        return 7
                    }
                })[1]
            })
        }
    })
      , y = u({
        "node_modules/core-js-pure/internals/function-call.js": function(r, n) {
            var o = s()
              , i = Function.prototype.call;
            n.exports = o ? i.bind(i) : function() {
                return i.apply(i, arguments)
            }
        }
    })
      , m = u({
        "node_modules/core-js-pure/internals/object-property-is-enumerable.js": function(r) {
            var n = {}.propertyIsEnumerable
              , o = Object.getOwnPropertyDescriptor;
            r.f = o && !n.call({
                1: 2
            }, 1) ? function(r) {
                var n = o(this, r);
                return !!n && n.enumerable
            }
            : n
        }
    })
      , g = u({
        "node_modules/core-js-pure/internals/create-property-descriptor.js": function(r, n) {
            n.exports = function(r, n) {
                return {
                    enumerable: !(1 & r),
                    configurable: !(2 & r),
                    writable: !(4 & r),
                    value: n
                }
            }
        }
    })
      , b = u({
        "node_modules/core-js-pure/internals/indexed-object.js": function(r, n) {
            var o = f()
              , i = c()
              , u = d()
              , a = Object
              , s = o("".split);
            n.exports = i(function() {
                return !a("z").propertyIsEnumerable(0)
            }) ? function(r) {
                return "String" === u(r) ? s(r, "") : a(r)
            }
            : a
        }
    })
      , j = u({
        "node_modules/core-js-pure/internals/is-null-or-undefined.js": function(r, n) {
            n.exports = function(r) {
                return null == r
            }
        }
    })
      , w = u({
        "node_modules/core-js-pure/internals/require-object-coercible.js": function(r, n) {
            var o = j()
              , i = TypeError;
            n.exports = function(r) {
                if (o(r))
                    throw new i("Can't call method on " + r);
                return r
            }
        }
    })
      , x = u({
        "node_modules/core-js-pure/internals/to-indexed-object.js": function(r, n) {
            var o = b()
              , i = w();
            n.exports = function(r) {
                return o(i(r))
            }
        }
    })
      , _ = u({
        "node_modules/core-js-pure/internals/is-object.js": function(r, n) {
            var o = v();
            n.exports = function(r) {
                return "object" == typeof r ? null !== r : o(r)
            }
        }
    })
      , E = u({
        "node_modules/core-js-pure/internals/path.js": function(r, n) {
            n.exports = {}
        }
    })
      , O = u({
        "node_modules/core-js-pure/internals/get-built-in.js": function(r, n) {
            var o = E()
              , i = a()
              , u = v()
              , c = function(r) {
                return u(r) ? r : void 0
            };
            n.exports = function(r, n) {
                return arguments.length < 2 ? c(o[r]) || c(i[r]) : o[r] && o[r][n] || i[r] && i[r][n]
            }
        }
    })
      , T = u({
        "node_modules/core-js-pure/internals/object-is-prototype-of.js": function(r, n) {
            n.exports = f()({}.isPrototypeOf)
        }
    })
      , k = u({
        "node_modules/core-js-pure/internals/environment-user-agent.js": function(r, n) {
            var o = a().navigator
              , i = o && o.userAgent;
            n.exports = i ? String(i) : ""
        }
    })
      , S = u({
        "node_modules/core-js-pure/internals/environment-v8-version.js": function(r, n) {
            var o, i, u = a(), c = k(), s = u.process, l = u.Deno, f = s && s.versions || l && l.version, d = f && f.v8;
            d && (i = (o = d.split("."))[0] > 0 && o[0] < 4 ? 1 : +(o[0] + o[1])),
            !i && c && (!(o = c.match(/Edge\/(\d+)/)) || o[1] >= 74) && (o = c.match(/Chrome\/(\d+)/)) && (i = +o[1]),
            n.exports = i
        }
    })
      , P = u({
        "node_modules/core-js-pure/internals/symbol-constructor-detection.js": function(r, o) {
            var i = S()
              , u = c()
              , s = a().String;
            o.exports = !!Object.getOwnPropertySymbols && !u(function() {
                var r = Symbol("symbol detection");
                return !s(r) || !n(Object(r), Symbol) || !Symbol.sham && i && i < 41
            })
        }
    })
      , C = u({
        "node_modules/core-js-pure/internals/use-symbol-as-uid.js": function(r, n) {
            n.exports = P() && !Symbol.sham && "symbol" == o(Symbol.iterator)
        }
    })
      , A = u({
        "node_modules/core-js-pure/internals/is-symbol.js": function(r, n) {
            var i = O()
              , u = v()
              , a = T()
              , c = C()
              , s = Object;
            n.exports = c ? function(r) {
                return "symbol" == (void 0 === r ? "undefined" : o(r))
            }
            : function(r) {
                var n = i("Symbol");
                return u(n) && a(n.prototype, s(r))
            }
        }
    })
      , I = u({
        "node_modules/core-js-pure/internals/try-to-string.js": function(r, n) {
            var o = String;
            n.exports = function(r) {
                try {
                    return o(r)
                } catch (r) {
                    return "Object"
                }
            }
        }
    })
      , R = u({
        "node_modules/core-js-pure/internals/a-callable.js": function(r, n) {
            var o = v()
              , i = I()
              , u = TypeError;
            n.exports = function(r) {
                if (o(r))
                    return r;
                throw new u(i(r) + " is not a function")
            }
        }
    })
      , L = u({
        "node_modules/core-js-pure/internals/get-method.js": function(r, n) {
            var o = R()
              , i = j();
            n.exports = function(r, n) {
                var u = r[n];
                return i(u) ? void 0 : o(u)
            }
        }
    })
      , M = u({
        "node_modules/core-js-pure/internals/ordinary-to-primitive.js": function(r, n) {
            var o = y()
              , i = v()
              , u = _()
              , a = TypeError;
            n.exports = function(r, n) {
                var c, s;
                if ("string" === n && i(c = r.toString) && !u(s = o(c, r)) || i(c = r.valueOf) && !u(s = o(c, r)) || "string" !== n && i(c = r.toString) && !u(s = o(c, r)))
                    return s;
                throw new a("Can't convert object to primitive value")
            }
        }
    })
      , N = u({
        "node_modules/core-js-pure/internals/is-pure.js": function(r, n) {
            n.exports = !0
        }
    })
      , D = u({
        "node_modules/core-js-pure/internals/define-global-property.js": function(r, n) {
            var o = a()
              , i = Object.defineProperty;
            n.exports = function(r, n) {
                try {
                    i(o, r, {
                        value: n,
                        configurable: !0,
                        writable: !0
                    })
                } catch (i) {
                    o[r] = n
                }
                return n
            }
        }
    })
      , B = u({
        "node_modules/core-js-pure/internals/shared-store.js": function(r, n) {
            var o = N()
              , i = a()
              , u = D()
              , c = "__core-js_shared__"
              , s = n.exports = i[c] || u(c, {});
            (s.versions || (s.versions = [])).push({
                version: "3.38.1",
                mode: o ? "pure" : "global",
                copyright: "© 2014-2024 Denis Pushkarev (zloirock.ru)",
                license: "https://github.com/zloirock/core-js/blob/v3.38.1/LICENSE",
                source: "https://github.com/zloirock/core-js"
            })
        }
    })
      , U = u({
        "node_modules/core-js-pure/internals/shared.js": function(r, n) {
            var o = B();
            n.exports = function(r, n) {
                return o[r] || (o[r] = n || {})
            }
        }
    })
      , F = u({
        "node_modules/core-js-pure/internals/to-object.js": function(r, n) {
            var o = w()
              , i = Object;
            n.exports = function(r) {
                return i(o(r))
            }
        }
    })
      , q = u({
        "node_modules/core-js-pure/internals/has-own-property.js": function(r, n) {
            var o = f()
              , i = F()
              , u = o({}.hasOwnProperty);
            n.exports = Object.hasOwn || function(r, n) {
                return u(i(r), n)
            }
        }
    })
      , H = u({
        "node_modules/core-js-pure/internals/uid.js": function(r, n) {
            var o = f()
              , i = 0
              , u = Math.random()
              , a = o(1. .toString);
            n.exports = function(r) {
                return "Symbol(" + (void 0 === r ? "" : r) + ")_" + a(++i + u, 36)
            }
        }
    })
      , z = u({
        "node_modules/core-js-pure/internals/well-known-symbol.js": function(r, n) {
            var o = a()
              , i = U()
              , u = q()
              , c = H()
              , s = P()
              , l = C()
              , f = o.Symbol
              , d = i("wks")
              , p = l ? f.for || f : f && f.withoutSetter || c;
            n.exports = function(r) {
                return u(d, r) || (d[r] = s && u(f, r) ? f[r] : p("Symbol." + r)),
                d[r]
            }
        }
    })
      , V = u({
        "node_modules/core-js-pure/internals/to-primitive.js": function(r, n) {
            var o = y()
              , i = _()
              , u = A()
              , a = L()
              , c = M()
              , s = z()
              , l = TypeError
              , f = s("toPrimitive");
            n.exports = function(r, n) {
                if (!i(r) || u(r))
                    return r;
                var s, d = a(r, f);
                if (d) {
                    if (void 0 === n && (n = "default"),
                    !i(s = o(d, r, n)) || u(s))
                        return s;
                    throw new l("Can't convert object to primitive value")
                }
                return void 0 === n && (n = "number"),
                c(r, n)
            }
        }
    })
      , G = u({
        "node_modules/core-js-pure/internals/to-property-key.js": function(r, n) {
            var o = V()
              , i = A();
            n.exports = function(r) {
                var n = o(r, "string");
                return i(n) ? n : n + ""
            }
        }
    })
      , J = u({
        "node_modules/core-js-pure/internals/document-create-element.js": function(r, n) {
            var o = a()
              , i = _()
              , u = o.document
              , c = i(u) && i(u.createElement);
            n.exports = function(r) {
                return c ? u.createElement(r) : {}
            }
        }
    })
      , K = u({
        "node_modules/core-js-pure/internals/ie8-dom-define.js": function(r, n) {
            var o = h()
              , i = c()
              , u = J();
            n.exports = !o && !i(function() {
                return 7 !== Object.defineProperty(u("div"), "a", {
                    get: function() {
                        return 7
                    }
                }).a
            })
        }
    })
      , W = u({
        "node_modules/core-js-pure/internals/object-get-own-property-descriptor.js": function(r) {
            var n = h()
              , o = y()
              , i = m()
              , u = g()
              , a = x()
              , c = G()
              , s = q()
              , l = K()
              , f = Object.getOwnPropertyDescriptor;
            r.f = n ? f : function(r, n) {
                if (r = a(r),
                n = c(n),
                l)
                    try {
                        return f(r, n)
                    } catch (r) {}
                if (s(r, n))
                    return u(!o(i.f, r, n), r[n])
            }
        }
    })
      , Y = u({
        "node_modules/core-js-pure/internals/is-forced.js": function(r, n) {
            var o = c()
              , i = v()
              , u = /#|\.prototype\./
              , a = function(r, n) {
                var u = l[s(r)];
                return u === d || u !== f && (i(n) ? o(n) : !!n)
            }
              , s = a.normalize = function(r) {
                return String(r).replace(u, ".").toLowerCase()
            }
              , l = a.data = {}
              , f = a.NATIVE = "N"
              , d = a.POLYFILL = "P";
            n.exports = a
        }
    })
      , X = u({
        "node_modules/core-js-pure/internals/function-bind-context.js": function(r, n) {
            var o = p()
              , i = R()
              , u = s()
              , a = o(o.bind);
            n.exports = function(r, n) {
                return i(r),
                void 0 === n ? r : u ? a(r, n) : function() {
                    return r.apply(n, arguments)
                }
            }
        }
    })
      , Q = u({
        "node_modules/core-js-pure/internals/v8-prototype-define-bug.js": function(r, n) {
            var o = h()
              , i = c();
            n.exports = o && i(function() {
                return 42 !== Object.defineProperty(function() {}, "prototype", {
                    value: 42,
                    writable: !1
                }).prototype
            })
        }
    })
      , $ = u({
        "node_modules/core-js-pure/internals/an-object.js": function(r, n) {
            var o = _()
              , i = String
              , u = TypeError;
            n.exports = function(r) {
                if (o(r))
                    return r;
                throw new u(i(r) + " is not an object")
            }
        }
    })
      , Z = u({
        "node_modules/core-js-pure/internals/object-define-property.js": function(r) {
            var n = h()
              , o = K()
              , i = Q()
              , u = $()
              , a = G()
              , c = TypeError
              , s = Object.defineProperty
              , l = Object.getOwnPropertyDescriptor
              , f = "enumerable"
              , d = "configurable"
              , p = "writable";
            r.f = n ? i ? function(r, n, o) {
                if (u(r),
                n = a(n),
                u(o),
                "function" == typeof r && "prototype" === n && "value"in o && p in o && !o[p]) {
                    var i = l(r, n);
                    i && i[p] && (r[n] = o.value,
                    o = {
                        configurable: d in o ? o[d] : i[d],
                        enumerable: f in o ? o[f] : i[f],
                        writable: !1
                    })
                }
                return s(r, n, o)
            }
            : s : function(r, n, i) {
                if (u(r),
                n = a(n),
                u(i),
                o)
                    try {
                        return s(r, n, i)
                    } catch (r) {}
                if ("get"in i || "set"in i)
                    throw new c("Accessors not supported");
                return "value"in i && (r[n] = i.value),
                r
            }
        }
    })
      , ee = u({
        "node_modules/core-js-pure/internals/create-non-enumerable-property.js": function(r, n) {
            var o = h()
              , i = Z()
              , u = g();
            n.exports = o ? function(r, n, o) {
                return i.f(r, n, u(1, o))
            }
            : function(r, n, o) {
                return r[n] = o,
                r
            }
        }
    })
      , et = u({
        "node_modules/core-js-pure/internals/export.js": function(r, i) {
            var u = a()
              , c = l()
              , s = p()
              , f = v()
              , d = W().f
              , h = Y()
              , y = E()
              , m = X()
              , g = ee()
              , b = q();
            B();
            var j = function(r) {
                var o = function(i, u, a) {
                    if (n(this, o)) {
                        switch (arguments.length) {
                        case 0:
                            return new r;
                        case 1:
                            return new r(i);
                        case 2:
                            return new r(i,u)
                        }
                        return new r(i,u,a)
                    }
                    return c(r, this, arguments)
                };
                return o.prototype = r.prototype,
                o
            };
            i.exports = function(r, n) {
                var i, a, c, l, p, v, w, x, _, E = r.target, O = r.global, T = r.stat, k = r.proto, S = O ? u : T ? u[E] : u[E] && u[E].prototype, P = O ? y : y[E] || g(y, E, {})[E], C = P.prototype;
                for (l in n)
                    a = !(i = h(O ? l : E + (T ? "." : "#") + l, r.forced)) && S && b(S, l),
                    v = P[l],
                    a && (w = r.dontCallGetSet ? (_ = d(S, l)) && _.value : S[l]),
                    p = a && w ? w : n[l],
                    (i || k || (void 0 === v ? "undefined" : o(v)) != (void 0 === p ? "undefined" : o(p))) && (x = r.bind && a ? m(p, u) : r.wrap && a ? j(p) : k && f(p) ? s(p) : p,
                    (r.sham || p && p.sham || v && v.sham) && g(x, "sham", !0),
                    g(P, l, x),
                    k && (b(y, c = E + "Prototype") || g(y, c, {}),
                    g(y[c], l, p),
                    r.real && C && (i || !C[l]) && g(C, l, p)))
            }
        }
    })
      , er = u({
        "node_modules/core-js-pure/internals/is-array.js": function(r, n) {
            var o = d();
            n.exports = Array.isArray || function(r) {
                return "Array" === o(r)
            }
        }
    })
      , en = u({
        "node_modules/core-js-pure/internals/math-trunc.js": function(r, n) {
            var o = Math.ceil
              , i = Math.floor;
            n.exports = Math.trunc || function(r) {
                var n = +r;
                return (n > 0 ? i : o)(n)
            }
        }
    })
      , eo = u({
        "node_modules/core-js-pure/internals/to-integer-or-infinity.js": function(r, n) {
            var o = en();
            n.exports = function(r) {
                var n = +r;
                return n != n || 0 === n ? 0 : o(n)
            }
        }
    })
      , ei = u({
        "node_modules/core-js-pure/internals/to-length.js": function(r, n) {
            var o = eo()
              , i = Math.min;
            n.exports = function(r) {
                var n = o(r);
                return n > 0 ? i(n, 0x1fffffffffffff) : 0
            }
        }
    })
      , eu = u({
        "node_modules/core-js-pure/internals/length-of-array-like.js": function(r, n) {
            var o = ei();
            n.exports = function(r) {
                return o(r.length)
            }
        }
    })
      , ea = u({
        "node_modules/core-js-pure/internals/does-not-exceed-safe-integer.js": function(r, n) {
            var o = TypeError;
            n.exports = function(r) {
                if (r > 0x1fffffffffffff)
                    throw o("Maximum allowed index exceeded");
                return r
            }
        }
    })
      , ec = u({
        "node_modules/core-js-pure/internals/create-property.js": function(r, n) {
            var o = h()
              , i = Z()
              , u = g();
            n.exports = function(r, n, a) {
                o ? i.f(r, n, u(0, a)) : r[n] = a
            }
        }
    })
      , es = u({
        "node_modules/core-js-pure/internals/to-string-tag-support.js": function(r, n) {
            var o = {};
            o[z()("toStringTag")] = "z",
            n.exports = "[object z]" === String(o)
        }
    })
      , el = u({
        "node_modules/core-js-pure/internals/classof.js": function(r, n) {
            var o = es()
              , i = v()
              , u = d()
              , a = z()("toStringTag")
              , c = Object
              , s = "Arguments" === u(function() {
                return arguments
            }());
            n.exports = o ? u : function(r) {
                var n, o, l;
                return void 0 === r ? "Undefined" : null === r ? "Null" : "string" == typeof (o = function(r, n) {
                    try {
                        return r[n]
                    } catch (r) {}
                }(n = c(r), a)) ? o : s ? u(n) : "Object" === (l = u(n)) && i(n.callee) ? "Arguments" : l
            }
        }
    })
      , ef = u({
        "node_modules/core-js-pure/internals/inspect-source.js": function(r, n) {
            var o = f()
              , i = v()
              , u = B()
              , a = o(Function.toString);
            i(u.inspectSource) || (u.inspectSource = function(r) {
                return a(r)
            }
            ),
            n.exports = u.inspectSource
        }
    })
      , ed = u({
        "node_modules/core-js-pure/internals/is-constructor.js": function(r, n) {
            var o = f()
              , i = c()
              , u = v()
              , a = el()
              , s = O()
              , l = ef()
              , d = function() {}
              , p = s("Reflect", "construct")
              , h = /^\s*(?:class|function)\b/
              , y = o(h.exec)
              , m = !h.test(d)
              , g = function(r) {
                if (!u(r))
                    return !1;
                try {
                    return p(d, [], r),
                    !0
                } catch (r) {
                    return !1
                }
            }
              , b = function(r) {
                if (!u(r))
                    return !1;
                switch (a(r)) {
                case "AsyncFunction":
                case "GeneratorFunction":
                case "AsyncGeneratorFunction":
                    return !1
                }
                try {
                    return m || !!y(h, l(r))
                } catch (r) {
                    return !0
                }
            };
            b.sham = !0,
            n.exports = !p || i(function() {
                var r;
                return g(g.call) || !g(Object) || !g(function() {
                    r = !0
                }) || r
            }) ? b : g
        }
    })
      , ep = u({
        "node_modules/core-js-pure/internals/array-species-constructor.js": function(r, n) {
            var o = er()
              , i = ed()
              , u = _()
              , a = z()("species")
              , c = Array;
            n.exports = function(r) {
                var n;
                return o(r) && (i(n = r.constructor) && (n === c || o(n.prototype)) || u(n) && null === (n = n[a])) && (n = void 0),
                void 0 === n ? c : n
            }
        }
    })
      , ev = u({
        "node_modules/core-js-pure/internals/array-species-create.js": function(r, n) {
            var o = ep();
            n.exports = function(r, n) {
                return new (o(r))(0 === n ? 0 : n)
            }
        }
    })
      , eh = u({
        "node_modules/core-js-pure/internals/array-method-has-species-support.js": function(r, n) {
            var o = c()
              , i = z()
              , u = S()
              , a = i("species");
            n.exports = function(r) {
                return u >= 51 || !o(function() {
                    var n = [];
                    return (n.constructor = {})[a] = function() {
                        return {
                            foo: 1
                        }
                    }
                    ,
                    1 !== n[r](Boolean).foo
                })
            }
        }
    })
      , ey = u({
        "node_modules/core-js-pure/modules/es.array.concat.js": function() {
            var r = et()
              , n = c()
              , o = er()
              , i = _()
              , u = F()
              , a = eu()
              , s = ea()
              , l = ec()
              , f = ev()
              , d = eh()
              , p = z()
              , v = S()
              , h = p("isConcatSpreadable")
              , y = v >= 51 || !n(function() {
                var r = [];
                return r[h] = !1,
                r.concat()[0] !== r
            })
              , m = function(r) {
                if (!i(r))
                    return !1;
                var n = r[h];
                return void 0 !== n ? !!n : o(r)
            };
            r({
                target: "Array",
                proto: !0,
                arity: 1,
                forced: !y || !d("concat")
            }, {
                concat: function(r) {
                    var n, o, i, c, d, p = u(this), v = f(p, 0), h = 0;
                    for (n = -1,
                    i = arguments.length; n < i; n++)
                        if (m(d = -1 === n ? p : arguments[n]))
                            for (s(h + (c = a(d))),
                            o = 0; o < c; o++,
                            h++)
                                o in d && l(v, h, d[o]);
                        else
                            s(h + 1),
                            l(v, h++, d);
                    return v.length = h,
                    v
                }
            })
        }
    })
      , em = u({
        "node_modules/core-js-pure/modules/es.object.to-string.js": function() {}
    })
      , eg = u({
        "node_modules/core-js-pure/internals/to-string.js": function(r, n) {
            var o = el()
              , i = String;
            n.exports = function(r) {
                if ("Symbol" === o(r))
                    throw TypeError("Cannot convert a Symbol value to a string");
                return i(r)
            }
        }
    })
      , eb = u({
        "node_modules/core-js-pure/internals/to-absolute-index.js": function(r, n) {
            var o = eo()
              , i = Math.max
              , u = Math.min;
            n.exports = function(r, n) {
                var a = o(r);
                return a < 0 ? i(a + n, 0) : u(a, n)
            }
        }
    })
      , ej = u({
        "node_modules/core-js-pure/internals/array-includes.js": function(r, n) {
            var o = x()
              , i = eb()
              , u = eu()
              , a = function(r) {
                return function(n, a, c) {
                    var s = o(n)
                      , l = u(s);
                    if (0 === l)
                        return !r && -1;
                    var f, d = i(c, l);
                    if (r && a != a) {
                        for (; l > d; )
                            if ((f = s[d++]) !== f)
                                return !0
                    } else
                        for (; l > d; d++)
                            if ((r || d in s) && s[d] === a)
                                return r || d || 0;
                    return !r && -1
                }
            };
            n.exports = {
                includes: a(!0),
                indexOf: a(!1)
            }
        }
    })
      , ew = u({
        "node_modules/core-js-pure/internals/hidden-keys.js": function(r, n) {
            n.exports = {}
        }
    })
      , ex = u({
        "node_modules/core-js-pure/internals/object-keys-internal.js": function(r, n) {
            var o = f()
              , i = q()
              , u = x()
              , a = ej().indexOf
              , c = ew()
              , s = o([].push);
            n.exports = function(r, n) {
                var o, l = u(r), f = 0, d = [];
                for (o in l)
                    !i(c, o) && i(l, o) && s(d, o);
                for (; n.length > f; )
                    i(l, o = n[f++]) && (~a(d, o) || s(d, o));
                return d
            }
        }
    })
      , e_ = u({
        "node_modules/core-js-pure/internals/enum-bug-keys.js": function(r, n) {
            n.exports = ["constructor", "hasOwnProperty", "isPrototypeOf", "propertyIsEnumerable", "toLocaleString", "toString", "valueOf"]
        }
    })
      , eE = u({
        "node_modules/core-js-pure/internals/object-keys.js": function(r, n) {
            var o = ex()
              , i = e_();
            n.exports = Object.keys || function(r) {
                return o(r, i)
            }
        }
    })
      , eO = u({
        "node_modules/core-js-pure/internals/object-define-properties.js": function(r) {
            var n = h()
              , o = Q()
              , i = Z()
              , u = $()
              , a = x()
              , c = eE();
            r.f = n && !o ? Object.defineProperties : function(r, n) {
                u(r);
                for (var o, s = a(n), l = c(n), f = l.length, d = 0; f > d; )
                    i.f(r, o = l[d++], s[o]);
                return r
            }
        }
    })
      , eT = u({
        "node_modules/core-js-pure/internals/html.js": function(r, n) {
            n.exports = O()("document", "documentElement")
        }
    })
      , ek = u({
        "node_modules/core-js-pure/internals/shared-key.js": function(r, n) {
            var o = U()
              , i = H()
              , u = o("keys");
            n.exports = function(r) {
                return u[r] || (u[r] = i(r))
            }
        }
    })
      , eS = u({
        "node_modules/core-js-pure/internals/object-create.js": function(r, n) {
            var o, i = $(), u = eO(), a = e_(), c = ew(), s = eT(), l = J(), f = ek(), d = "prototype", p = "script", v = f("IE_PROTO"), h = function() {}, y = function(r) {
                return "<" + p + ">" + r + "</" + p + ">"
            }, m = function(r) {
                r.write(y("")),
                r.close();
                var n = r.parentWindow.Object;
                return r = null,
                n
            }, g = function() {
                try {
                    o = new ActiveXObject("htmlfile")
                } catch (r) {}
                g = "undefined" != typeof document ? document.domain && o ? m(o) : ((n = l("iframe")).style.display = "none",
                s.appendChild(n),
                n.src = String("java" + p + ":"),
                (r = n.contentWindow.document).open(),
                r.write(y("document.F=Object")),
                r.close(),
                r.F) : m(o);
                for (var r, n, i = a.length; i--; )
                    delete g[d][a[i]];
                return g()
            };
            c[v] = !0,
            n.exports = Object.create || function(r, n) {
                var o;
                return null !== r ? (h[d] = i(r),
                o = new h,
                h[d] = null,
                o[v] = r) : o = g(),
                void 0 === n ? o : u.f(o, n)
            }
        }
    })
      , eP = u({
        "node_modules/core-js-pure/internals/object-get-own-property-names.js": function(r) {
            var n = ex()
              , o = e_().concat("length", "prototype");
            r.f = Object.getOwnPropertyNames || function(r) {
                return n(r, o)
            }
        }
    })
      , eC = u({
        "node_modules/core-js-pure/internals/array-slice.js": function(r, n) {
            n.exports = f()([].slice)
        }
    })
      , eA = u({
        "node_modules/core-js-pure/internals/object-get-own-property-names-external.js": function(r, n) {
            var o = d()
              , i = x()
              , u = eP().f
              , a = eC()
              , c = "object" == typeof window && window && Object.getOwnPropertyNames ? Object.getOwnPropertyNames(window) : [];
            n.exports.f = function(r) {
                return c && "Window" === o(r) ? function(r) {
                    try {
                        return u(r)
                    } catch (r) {
                        return a(c)
                    }
                }(r) : u(i(r))
            }
        }
    })
      , eI = u({
        "node_modules/core-js-pure/internals/object-get-own-property-symbols.js": function(r) {
            r.f = Object.getOwnPropertySymbols
        }
    })
      , eR = u({
        "node_modules/core-js-pure/internals/define-built-in.js": function(r, n) {
            var o = ee();
            n.exports = function(r, n, i, u) {
                return u && u.enumerable ? r[n] = i : o(r, n, i),
                r
            }
        }
    })
      , eL = u({
        "node_modules/core-js-pure/internals/define-built-in-accessor.js": function(r, n) {
            var o = Z();
            n.exports = function(r, n, i) {
                return o.f(r, n, i)
            }
        }
    })
      , eM = u({
        "node_modules/core-js-pure/internals/well-known-symbol-wrapped.js": function(r) {
            r.f = z()
        }
    })
      , eN = u({
        "node_modules/core-js-pure/internals/well-known-symbol-define.js": function(r, n) {
            var o = E()
              , i = q()
              , u = eM()
              , a = Z().f;
            n.exports = function(r) {
                var n = o.Symbol || (o.Symbol = {});
                i(n, r) || a(n, r, {
                    value: u.f(r)
                })
            }
        }
    })
      , eD = u({
        "node_modules/core-js-pure/internals/symbol-define-to-primitive.js": function(r, n) {
            var o = y()
              , i = O()
              , u = z()
              , a = eR();
            n.exports = function() {
                var r = i("Symbol")
                  , n = r && r.prototype
                  , c = n && n.valueOf
                  , s = u("toPrimitive");
                n && !n[s] && a(n, s, function(r) {
                    return o(c, this)
                }, {
                    arity: 1
                })
            }
        }
    })
      , eB = u({
        "node_modules/core-js-pure/internals/object-to-string.js": function(r, n) {
            var o = es()
              , i = el();
            n.exports = o ? ({}).toString : function() {
                return "[object " + i(this) + "]"
            }
        }
    })
      , eU = u({
        "node_modules/core-js-pure/internals/set-to-string-tag.js": function(r, n) {
            var o = es()
              , i = Z().f
              , u = ee()
              , a = q()
              , c = eB()
              , s = z()("toStringTag");
            n.exports = function(r, n, l, f) {
                var d = l ? r : r && r.prototype;
                d && (a(d, s) || i(d, s, {
                    configurable: !0,
                    value: n
                }),
                f && !o && u(d, "toString", c))
            }
        }
    })
      , eF = u({
        "node_modules/core-js-pure/internals/weak-map-basic-detection.js": function(r, n) {
            var o = a()
              , i = v()
              , u = o.WeakMap;
            n.exports = i(u) && /native code/.test(String(u))
        }
    })
      , eq = u({
        "node_modules/core-js-pure/internals/internal-state.js": function(r, n) {
            var o, i, u, c, s, l = eF(), f = a(), d = _(), p = ee(), v = q(), h = B(), y = ek(), m = ew(), g = "Object already initialized", b = f.TypeError, j = f.WeakMap;
            l || h.state ? ((c = h.state || (h.state = new j)).get = c.get,
            c.has = c.has,
            c.set = c.set,
            o = function(r, n) {
                if (c.has(r))
                    throw new b(g);
                return n.facade = r,
                c.set(r, n),
                n
            }
            ,
            i = function(r) {
                return c.get(r) || {}
            }
            ,
            u = function(r) {
                return c.has(r)
            }
            ) : (m[s = y("state")] = !0,
            o = function(r, n) {
                if (v(r, s))
                    throw new b(g);
                return n.facade = r,
                p(r, s, n),
                n
            }
            ,
            i = function(r) {
                return v(r, s) ? r[s] : {}
            }
            ,
            u = function(r) {
                return v(r, s)
            }
            ),
            n.exports = {
                set: o,
                get: i,
                has: u,
                enforce: function(r) {
                    return u(r) ? i(r) : o(r, {})
                },
                getterFor: function(r) {
                    return function(n) {
                        var o;
                        if (!d(n) || (o = i(n)).type !== r)
                            throw new b("Incompatible receiver, " + r + " required");
                        return o
                    }
                }
            }
        }
    })
      , eH = u({
        "node_modules/core-js-pure/internals/array-iteration.js": function(r, n) {
            var o = X()
              , i = f()
              , u = b()
              , a = F()
              , c = eu()
              , s = ev()
              , l = i([].push)
              , d = function(r) {
                var n = 1 === r
                  , i = 2 === r
                  , f = 3 === r
                  , d = 4 === r
                  , p = 6 === r
                  , v = 7 === r
                  , h = 5 === r || p;
                return function(y, m, g, b) {
                    for (var j, w, x = a(y), _ = u(x), E = c(_), O = o(m, g), T = 0, k = b || s, S = n ? k(y, E) : i || v ? k(y, 0) : void 0; E > T; T++)
                        if ((h || T in _) && (w = O(j = _[T], T, x),
                        r)) {
                            if (n)
                                S[T] = w;
                            else if (w)
                                switch (r) {
                                case 3:
                                    return !0;
                                case 5:
                                    return j;
                                case 6:
                                    return T;
                                case 2:
                                    l(S, j)
                                }
                            else
                                switch (r) {
                                case 4:
                                    return !1;
                                case 7:
                                    l(S, j)
                                }
                        }
                    return p ? -1 : f || d ? d : S
                }
            };
            n.exports = {
                forEach: d(0),
                map: d(1),
                filter: d(2),
                some: d(3),
                every: d(4),
                find: d(5),
                findIndex: d(6),
                filterReject: d(7)
            }
        }
    })
      , ez = u({
        "node_modules/core-js-pure/modules/es.symbol.constructor.js": function() {
            var r = et()
              , o = a()
              , i = y()
              , u = f()
              , s = N()
              , l = h()
              , d = P()
              , p = c()
              , v = q()
              , b = T()
              , j = $()
              , w = x()
              , _ = G()
              , E = eg()
              , O = g()
              , k = eS()
              , S = eE()
              , C = eP()
              , A = eA()
              , I = eI()
              , R = W()
              , L = Z()
              , M = eO()
              , D = m()
              , B = eR()
              , F = eL()
              , V = U()
              , J = ek()
              , K = ew()
              , Y = H()
              , X = z()
              , Q = eM()
              , ee = eN()
              , er = eD()
              , en = eU()
              , eo = eq()
              , ei = eH().forEach
              , eu = J("hidden")
              , ea = "Symbol"
              , ec = "prototype"
              , es = eo.set
              , el = eo.getterFor(ea)
              , ef = Object[ec]
              , ed = o.Symbol
              , ep = ed && ed[ec]
              , ev = o.RangeError
              , eh = o.TypeError
              , ey = o.QObject
              , em = R.f
              , eb = L.f
              , ej = A.f
              , ex = D.f
              , e_ = u([].push)
              , eT = V("symbols")
              , eC = V("op-symbols")
              , eB = V("wks")
              , eF = !ey || !ey[ec] || !ey[ec].findChild
              , ez = function(r, n, o) {
                var i = em(ef, n);
                i && delete ef[n],
                eb(r, n, o),
                i && r !== ef && eb(ef, n, i)
            }
              , eV = l && p(function() {
                return 7 !== k(eb({}, "a", {
                    get: function() {
                        return eb(this, "a", {
                            value: 7
                        }).a
                    }
                })).a
            }) ? ez : eb
              , eG = function(r, n) {
                var o = eT[r] = k(ep);
                return es(o, {
                    type: ea,
                    tag: r,
                    description: n
                }),
                l || (o.description = n),
                o
            }
              , eJ = function(r, n, o) {
                r === ef && eJ(eC, n, o),
                j(r);
                var i = _(n);
                return j(o),
                v(eT, i) ? (o.enumerable ? (v(r, eu) && r[eu][i] && (r[eu][i] = !1),
                o = k(o, {
                    enumerable: O(0, !1)
                })) : (v(r, eu) || eb(r, eu, O(1, k(null))),
                r[eu][i] = !0),
                eV(r, i, o)) : eb(r, i, o)
            }
              , eK = function(r, n) {
                j(r);
                var o = w(n);
                return ei(S(o).concat(eQ(o)), function(n) {
                    l && !i(eW, o, n) || eJ(r, n, o[n])
                }),
                r
            }
              , eW = function(r) {
                var n = _(r)
                  , o = i(ex, this, n);
                return !(this === ef && v(eT, n) && !v(eC, n)) && (!(o || !v(this, n) || !v(eT, n) || v(this, eu) && this[eu][n]) || o)
            }
              , eY = function(r, n) {
                var o = w(r)
                  , i = _(n);
                if (o !== ef || !v(eT, i) || v(eC, i)) {
                    var u = em(o, i);
                    return !u || !v(eT, i) || v(o, eu) && o[eu][i] || (u.enumerable = !0),
                    u
                }
            }
              , eX = function(r) {
                var n = ej(w(r))
                  , o = [];
                return ei(n, function(r) {
                    v(eT, r) || v(K, r) || e_(o, r)
                }),
                o
            }
              , eQ = function(r) {
                var n = r === ef
                  , o = ej(n ? eC : w(r))
                  , i = [];
                return ei(o, function(r) {
                    v(eT, r) && (!n || v(ef, r)) && e_(i, eT[r])
                }),
                i
            };
            d || (B(ep = (ed = function() {
                if (b(ep, this))
                    throw new eh("Symbol is not a constructor");
                var r = arguments.length && void 0 !== arguments[0] ? E(arguments[0]) : void 0
                  , u = Y(r)
                  , a = function(r) {
                    var c = void 0 === this ? o : this;
                    c === ef && i(a, eC, r),
                    v(c, eu) && v(c[eu], u) && (c[eu][u] = !1);
                    var s = O(1, r);
                    try {
                        eV(c, u, s)
                    } catch (r) {
                        if (!n(r, ev))
                            throw r;
                        ez(c, u, s)
                    }
                };
                return l && eF && eV(ef, u, {
                    configurable: !0,
                    set: a
                }),
                eG(u, r)
            }
            )[ec], "toString", function() {
                return el(this).tag
            }),
            B(ed, "withoutSetter", function(r) {
                return eG(Y(r), r)
            }),
            D.f = eW,
            L.f = eJ,
            M.f = eK,
            R.f = eY,
            C.f = A.f = eX,
            I.f = eQ,
            Q.f = function(r) {
                return eG(X(r), r)
            }
            ,
            l && (F(ep, "description", {
                configurable: !0,
                get: function() {
                    return el(this).description
                }
            }),
            s || B(ef, "propertyIsEnumerable", eW, {
                unsafe: !0
            }))),
            r({
                global: !0,
                constructor: !0,
                wrap: !0,
                forced: !d,
                sham: !d
            }, {
                Symbol: ed
            }),
            ei(S(eB), function(r) {
                ee(r)
            }),
            r({
                target: ea,
                stat: !0,
                forced: !d
            }, {
                useSetter: function() {
                    eF = !0
                },
                useSimple: function() {
                    eF = !1
                }
            }),
            r({
                target: "Object",
                stat: !0,
                forced: !d,
                sham: !l
            }, {
                create: function(r, n) {
                    return void 0 === n ? k(r) : eK(k(r), n)
                },
                defineProperty: eJ,
                defineProperties: eK,
                getOwnPropertyDescriptor: eY
            }),
            r({
                target: "Object",
                stat: !0,
                forced: !d
            }, {
                getOwnPropertyNames: eX
            }),
            er(),
            en(ed, ea),
            K[eu] = !0
        }
    })
      , eV = u({
        "node_modules/core-js-pure/internals/symbol-registry-detection.js": function(r, n) {
            n.exports = P() && !!Symbol.for && !!Symbol.keyFor
        }
    })
      , eG = u({
        "node_modules/core-js-pure/modules/es.symbol.for.js": function() {
            var r = et()
              , n = O()
              , o = q()
              , i = eg()
              , u = U()
              , a = eV()
              , c = u("string-to-symbol-registry")
              , s = u("symbol-to-string-registry");
            r({
                target: "Symbol",
                stat: !0,
                forced: !a
            }, {
                for: function(r) {
                    var u = i(r);
                    if (o(c, u))
                        return c[u];
                    var a = n("Symbol")(u);
                    return c[u] = a,
                    s[a] = u,
                    a
                }
            })
        }
    })
      , eJ = u({
        "node_modules/core-js-pure/modules/es.symbol.key-for.js": function() {
            var r = et()
              , n = q()
              , o = A()
              , i = I()
              , u = U()
              , a = eV()
              , c = u("symbol-to-string-registry");
            r({
                target: "Symbol",
                stat: !0,
                forced: !a
            }, {
                keyFor: function(r) {
                    if (!o(r))
                        throw TypeError(i(r) + " is not a symbol");
                    if (n(c, r))
                        return c[r]
                }
            })
        }
    })
      , eK = u({
        "node_modules/core-js-pure/internals/get-json-replacer-function.js": function(r, n) {
            var o = f()
              , i = er()
              , u = v()
              , a = d()
              , c = eg()
              , s = o([].push);
            n.exports = function(r) {
                if (u(r))
                    return r;
                if (i(r)) {
                    for (var n = r.length, o = [], l = 0; l < n; l++) {
                        var f = r[l];
                        "string" == typeof f ? s(o, f) : "number" != typeof f && "Number" !== a(f) && "String" !== a(f) || s(o, c(f))
                    }
                    var d = o.length
                      , p = !0;
                    return function(r, n) {
                        if (p)
                            return p = !1,
                            n;
                        if (i(this))
                            return n;
                        for (var u = 0; u < d; u++)
                            if (o[u] === r)
                                return n
                    }
                }
            }
        }
    })
      , eW = u({
        "node_modules/core-js-pure/modules/es.json.stringify.js": function() {
            var r = et()
              , n = O()
              , o = l()
              , i = y()
              , u = f()
              , a = c()
              , s = v()
              , d = A()
              , p = eC()
              , h = eK()
              , m = P()
              , g = String
              , b = n("JSON", "stringify")
              , j = u(/./.exec)
              , w = u("".charAt)
              , x = u("".charCodeAt)
              , _ = u("".replace)
              , E = u(1. .toString)
              , T = /[\uD800-\uDFFF]/g
              , k = /^[\uD800-\uDBFF]$/
              , S = /^[\uDC00-\uDFFF]$/
              , C = !m || a(function() {
                var r = n("Symbol")("stringify detection");
                return "[null]" !== b([r]) || "{}" !== b({
                    a: r
                }) || "{}" !== b(Object(r))
            })
              , I = a(function() {
                return '"\udf06\ud834"' !== b("\udf06\ud834") || '"\udead"' !== b("\udead")
            })
              , R = function(r, n) {
                var u = p(arguments)
                  , a = h(n);
                if (s(a) || void 0 !== r && !d(r))
                    return u[1] = function(r, n) {
                        if (s(a) && (n = i(a, this, g(r), n)),
                        !d(n))
                            return n
                    }
                    ,
                    o(b, null, u)
            }
              , L = function(r, n, o) {
                var i = w(o, n - 1)
                  , u = w(o, n + 1);
                return j(k, r) && !j(S, u) || j(S, r) && !j(k, i) ? "\\u" + E(x(r, 0), 16) : r
            };
            b && r({
                target: "JSON",
                stat: !0,
                arity: 3,
                forced: C || I
            }, {
                stringify: function(r, n, i) {
                    var u = p(arguments)
                      , a = o(C ? R : b, null, u);
                    return I && "string" == typeof a ? _(a, T, L) : a
                }
            })
        }
    })
      , eY = u({
        "node_modules/core-js-pure/modules/es.object.get-own-property-symbols.js": function() {
            var r = et()
              , n = P()
              , o = c()
              , i = eI()
              , u = F();
            r({
                target: "Object",
                stat: !0,
                forced: !n || o(function() {
                    i.f(1)
                })
            }, {
                getOwnPropertySymbols: function(r) {
                    var n = i.f;
                    return n ? n(u(r)) : []
                }
            })
        }
    })
      , eX = u({
        "node_modules/core-js-pure/modules/es.symbol.js": function() {
            ez(),
            eG(),
            eJ(),
            eW(),
            eY()
        }
    })
      , eQ = u({
        "node_modules/core-js-pure/modules/es.symbol.async-iterator.js": function() {
            eN()("asyncIterator")
        }
    })
      , e$ = u({
        "node_modules/core-js-pure/modules/es.symbol.description.js": function() {}
    })
      , eZ = u({
        "node_modules/core-js-pure/modules/es.symbol.has-instance.js": function() {
            eN()("hasInstance")
        }
    })
      , e0 = u({
        "node_modules/core-js-pure/modules/es.symbol.is-concat-spreadable.js": function() {
            eN()("isConcatSpreadable")
        }
    })
      , e1 = u({
        "node_modules/core-js-pure/modules/es.symbol.iterator.js": function() {
            eN()("iterator")
        }
    })
      , e2 = u({
        "node_modules/core-js-pure/modules/es.symbol.match.js": function() {
            eN()("match")
        }
    })
      , e5 = u({
        "node_modules/core-js-pure/modules/es.symbol.match-all.js": function() {
            eN()("matchAll")
        }
    })
      , e3 = u({
        "node_modules/core-js-pure/modules/es.symbol.replace.js": function() {
            eN()("replace")
        }
    })
      , e6 = u({
        "node_modules/core-js-pure/modules/es.symbol.search.js": function() {
            eN()("search")
        }
    })
      , e4 = u({
        "node_modules/core-js-pure/modules/es.symbol.species.js": function() {
            eN()("species")
        }
    })
      , e8 = u({
        "node_modules/core-js-pure/modules/es.symbol.split.js": function() {
            eN()("split")
        }
    })
      , e7 = u({
        "node_modules/core-js-pure/modules/es.symbol.to-primitive.js": function() {
            var r = eN()
              , n = eD();
            r("toPrimitive"),
            n()
        }
    })
      , e9 = u({
        "node_modules/core-js-pure/modules/es.symbol.to-string-tag.js": function() {
            var r = O()
              , n = eN()
              , o = eU();
            n("toStringTag"),
            o(r("Symbol"), "Symbol")
        }
    })
      , te = u({
        "node_modules/core-js-pure/modules/es.symbol.unscopables.js": function() {
            eN()("unscopables")
        }
    })
      , tt = u({
        "node_modules/core-js-pure/modules/es.json.to-string-tag.js": function() {
            var r = a();
            eU()(r.JSON, "JSON", !0)
        }
    })
      , tr = u({
        "node_modules/core-js-pure/modules/es.math.to-string-tag.js": function() {}
    })
      , tn = u({
        "node_modules/core-js-pure/modules/es.reflect.to-string-tag.js": function() {}
    })
      , to = u({
        "node_modules/core-js-pure/es/symbol/index.js": function(r, n) {
            ey(),
            em(),
            eX(),
            eQ(),
            e$(),
            eZ(),
            e0(),
            e1(),
            e2(),
            e5(),
            e3(),
            e6(),
            e4(),
            e8(),
            e7(),
            e9(),
            te(),
            tt(),
            tr(),
            tn(),
            n.exports = E().Symbol
        }
    })
      , ti = u({
        "node_modules/core-js-pure/internals/add-to-unscopables.js": function(r, n) {
            n.exports = function() {}
        }
    })
      , tu = u({
        "node_modules/core-js-pure/internals/iterators.js": function(r, n) {
            n.exports = {}
        }
    })
      , ta = u({
        "node_modules/core-js-pure/internals/function-name.js": function(r, n) {
            var o = h()
              , i = q()
              , u = Function.prototype
              , a = o && Object.getOwnPropertyDescriptor
              , c = i(u, "name")
              , s = c && (!o || o && a(u, "name").configurable);
            n.exports = {
                EXISTS: c,
                PROPER: c && "something" === (function() {}
                ).name,
                CONFIGURABLE: s
            }
        }
    })
      , tc = u({
        "node_modules/core-js-pure/internals/correct-prototype-getter.js": function(r, n) {
            n.exports = !c()(function() {
                function r() {}
                return r.prototype.constructor = null,
                Object.getPrototypeOf(new r) !== r.prototype
            })
        }
    })
      , ts = u({
        "node_modules/core-js-pure/internals/object-get-prototype-of.js": function(r, o) {
            var i = q()
              , u = v()
              , a = F()
              , c = ek()
              , s = tc()
              , l = c("IE_PROTO")
              , f = Object
              , d = f.prototype;
            o.exports = s ? f.getPrototypeOf : function(r) {
                var o = a(r);
                if (i(o, l))
                    return o[l];
                var c = o.constructor;
                return u(c) && n(o, c) ? c.prototype : n(o, f) ? d : null
            }
        }
    })
      , tl = u({
        "node_modules/core-js-pure/internals/iterators-core.js": function(r, n) {
            var o, i, u, a = c(), s = v(), l = _(), f = eS(), d = ts(), p = eR(), h = z(), y = N(), m = h("iterator"), g = !1;
            [].keys && ("next"in (u = [].keys()) ? (i = d(d(u))) !== Object.prototype && (o = i) : g = !0),
            !l(o) || a(function() {
                var r = {};
                return o[m].call(r) !== r
            }) ? o = {} : y && (o = f(o)),
            s(o[m]) || p(o, m, function() {
                return this
            }),
            n.exports = {
                IteratorPrototype: o,
                BUGGY_SAFARI_ITERATORS: g
            }
        }
    })
      , tf = u({
        "node_modules/core-js-pure/internals/iterator-create-constructor.js": function(r, n) {
            var o = tl().IteratorPrototype
              , i = eS()
              , u = g()
              , a = eU()
              , c = tu()
              , s = function() {
                return this
            };
            n.exports = function(r, n, l, f) {
                var d = n + " Iterator";
                return r.prototype = i(o, {
                    next: u(+!f, l)
                }),
                a(r, d, !1, !0),
                c[d] = s,
                r
            }
        }
    })
      , td = u({
        "node_modules/core-js-pure/internals/function-uncurry-this-accessor.js": function(r, n) {
            var o = f()
              , i = R();
            n.exports = function(r, n, u) {
                try {
                    return o(i(Object.getOwnPropertyDescriptor(r, n)[u]))
                } catch (r) {}
            }
        }
    })
      , tp = u({
        "node_modules/core-js-pure/internals/is-possible-prototype.js": function(r, n) {
            var o = _();
            n.exports = function(r) {
                return o(r) || null === r
            }
        }
    })
      , tv = u({
        "node_modules/core-js-pure/internals/a-possible-prototype.js": function(r, n) {
            var o = tp()
              , i = String
              , u = TypeError;
            n.exports = function(r) {
                if (o(r))
                    return r;
                throw new u("Can't set " + i(r) + " as a prototype")
            }
        }
    })
      , th = u({
        "node_modules/core-js-pure/internals/object-set-prototype-of.js": function(r, o) {
            var i = td()
              , u = _()
              , a = w()
              , c = tv();
            o.exports = Object.setPrototypeOf || ("__proto__"in {} ? function() {
                var r, o = !1, s = {};
                try {
                    (r = i(Object.prototype, "__proto__", "set"))(s, []),
                    o = n(s, Array)
                } catch (r) {}
                return function(n, i) {
                    return a(n),
                    c(i),
                    u(n) && (o ? r(n, i) : n.__proto__ = i),
                    n
                }
            }() : void 0)
        }
    })
      , ty = u({
        "node_modules/core-js-pure/internals/iterator-define.js": function(r, n) {
            var o = et()
              , i = y()
              , u = N()
              , a = ta()
              , c = v()
              , s = tf()
              , l = ts()
              , f = th()
              , d = eU()
              , p = ee()
              , h = eR()
              , m = z()
              , g = tu()
              , b = tl()
              , j = a.PROPER
              , w = a.CONFIGURABLE
              , x = b.IteratorPrototype
              , _ = b.BUGGY_SAFARI_ITERATORS
              , E = m("iterator")
              , O = "keys"
              , T = "values"
              , k = "entries"
              , S = function() {
                return this
            };
            n.exports = function(r, n, a, v, y, m, b) {
                s(a, n, v);
                var P, C, A, I = function(r) {
                    if (r === y && D)
                        return D;
                    if (!_ && r && r in M)
                        return M[r];
                    switch (r) {
                    case O:
                    case T:
                    case k:
                        return function() {
                            return new a(this,r)
                        }
                    }
                    return function() {
                        return new a(this)
                    }
                }, R = n + " Iterator", L = !1, M = r.prototype, N = M[E] || M["@@iterator"] || y && M[y], D = !_ && N || I(y), B = "Array" === n && M.entries || N;
                if (B && (P = l(B.call(new r))) !== Object.prototype && P.next && (u || l(P) === x || (f ? f(P, x) : c(P[E]) || h(P, E, S)),
                d(P, R, !0, !0),
                u && (g[R] = S)),
                j && y === T && N && N.name !== T && (!u && w ? p(M, "name", T) : (L = !0,
                D = function() {
                    return i(N, this)
                }
                )),
                y) {
                    if (C = {
                        values: I(T),
                        keys: m ? D : I(O),
                        entries: I(k)
                    },
                    b)
                        for (A in C)
                            !_ && !L && A in M || h(M, A, C[A]);
                    else
                        o({
                            target: n,
                            proto: !0,
                            forced: _ || L
                        }, C)
                }
                return u && !b || M[E] === D || h(M, E, D, {
                    name: y
                }),
                g[n] = D,
                C
            }
        }
    })
      , tm = u({
        "node_modules/core-js-pure/internals/create-iter-result-object.js": function(r, n) {
            n.exports = function(r, n) {
                return {
                    value: r,
                    done: n
                }
            }
        }
    })
      , tg = u({
        "node_modules/core-js-pure/modules/es.array.iterator.js": function(r, n) {
            var o = x()
              , i = ti()
              , u = tu()
              , a = eq()
              , c = Z().f
              , s = ty()
              , l = tm()
              , f = N()
              , d = h()
              , p = "Array Iterator"
              , v = a.set
              , y = a.getterFor(p);
            n.exports = s(Array, "Array", function(r, n) {
                v(this, {
                    type: p,
                    target: o(r),
                    index: 0,
                    kind: n
                })
            }, function() {
                var r = y(this)
                  , n = r.target
                  , o = r.index++;
                if (!n || o >= n.length)
                    return r.target = null,
                    l(void 0, !0);
                switch (r.kind) {
                case "keys":
                    return l(o, !1);
                case "values":
                    return l(n[o], !1)
                }
                return l([o, n[o]], !1)
            }, "values");
            var m = u.Arguments = u.Array;
            if (i("keys"),
            i("values"),
            i("entries"),
            !f && d && "values" !== m.name)
                try {
                    c(m, "name", {
                        value: "values"
                    })
                } catch (r) {}
        }
    })
      , tb = u({
        "node_modules/core-js-pure/internals/dom-iterables.js": function(r, n) {
            n.exports = {
                CSSRuleList: 0,
                CSSStyleDeclaration: 0,
                CSSValueList: 0,
                ClientRectList: 0,
                DOMRectList: 0,
                DOMStringList: 0,
                DOMTokenList: 1,
                DataTransferItemList: 0,
                FileList: 0,
                HTMLAllCollection: 0,
                HTMLCollection: 0,
                HTMLFormElement: 0,
                HTMLSelectElement: 0,
                MediaList: 0,
                MimeTypeArray: 0,
                NamedNodeMap: 0,
                NodeList: 1,
                PaintRequestList: 0,
                Plugin: 0,
                PluginArray: 0,
                SVGLengthList: 0,
                SVGNumberList: 0,
                SVGPathSegList: 0,
                SVGPointList: 0,
                SVGStringList: 0,
                SVGTransformList: 0,
                SourceBufferList: 0,
                StyleSheetList: 0,
                TextTrackCueList: 0,
                TextTrackList: 0,
                TouchList: 0
            }
        }
    })
      , tj = u({
        "node_modules/core-js-pure/modules/web.dom-collections.iterator.js": function() {
            tg();
            var r, n = tb(), o = a(), i = eU(), u = tu();
            for (r in n)
                i(o[r], r),
                u[r] = u.Array
        }
    })
      , tw = u({
        "node_modules/core-js-pure/stable/symbol/index.js": function(r, n) {
            var o = to();
            tj(),
            n.exports = o
        }
    })
      , tx = u({
        "node_modules/core-js-pure/internals/string-multibyte.js": function(r, n) {
            var o = f()
              , i = eo()
              , u = eg()
              , a = w()
              , c = o("".charAt)
              , s = o("".charCodeAt)
              , l = o("".slice)
              , d = function(r) {
                return function(n, o) {
                    var f, d, p = u(a(n)), v = i(o), h = p.length;
                    return v < 0 || v >= h ? r ? "" : void 0 : (f = s(p, v)) < 55296 || f > 56319 || v + 1 === h || (d = s(p, v + 1)) < 56320 || d > 57343 ? r ? c(p, v) : f : r ? l(p, v, v + 2) : d - 56320 + (f - 55296 << 10) + 65536
                }
            };
            n.exports = {
                codeAt: d(!1),
                charAt: d(!0)
            }
        }
    })
      , t_ = u({
        "node_modules/core-js-pure/modules/es.string.iterator.js": function() {
            var r = tx().charAt
              , n = eg()
              , o = eq()
              , i = ty()
              , u = tm()
              , a = "String Iterator"
              , c = o.set
              , s = o.getterFor(a);
            i(String, "String", function(r) {
                c(this, {
                    type: a,
                    string: n(r),
                    index: 0
                })
            }, function() {
                var n, o = s(this), i = o.string, a = o.index;
                return a >= i.length ? u(void 0, !0) : (n = r(i, a),
                o.index += n.length,
                u(n, !1))
            })
        }
    })
      , tE = u({
        "node_modules/core-js-pure/es/symbol/iterator.js": function(r, n) {
            tg(),
            em(),
            t_(),
            e1(),
            n.exports = eM().f("iterator")
        }
    })
      , tO = u({
        "node_modules/core-js-pure/stable/symbol/iterator.js": function(r, n) {
            var o = tE();
            tj(),
            n.exports = o
        }
    })
      , tT = u({
        "node_modules/core-js-pure/modules/es.object.keys.js": function() {
            var r = et()
              , n = F()
              , o = eE();
            r({
                target: "Object",
                stat: !0,
                forced: c()(function() {
                    o(1)
                })
            }, {
                keys: function(r) {
                    return o(n(r))
                }
            })
        }
    })
      , tk = u({
        "node_modules/core-js-pure/es/object/keys.js": function(r, n) {
            tT(),
            n.exports = E().Object.keys
        }
    })
      , tS = u({
        "node_modules/core-js-pure/stable/object/keys.js": function(r, n) {
            n.exports = tk()
        }
    })
      , tP = u({
        "node_modules/core-js-pure/es/object/get-own-property-symbols.js": function(r, n) {
            eX(),
            n.exports = E().Object.getOwnPropertySymbols
        }
    })
      , tC = u({
        "node_modules/core-js-pure/stable/object/get-own-property-symbols.js": function(r, n) {
            n.exports = tP()
        }
    })
      , tA = u({
        "node_modules/core-js-pure/modules/es.array.filter.js": function() {
            var r = et()
              , n = eH().filter;
            r({
                target: "Array",
                proto: !0,
                forced: !eh()("filter")
            }, {
                filter: function(r) {
                    return n(this, r, arguments.length > 1 ? arguments[1] : void 0)
                }
            })
        }
    })
      , tI = u({
        "node_modules/core-js-pure/internals/get-built-in-prototype-method.js": function(r, n) {
            var o = a()
              , i = E();
            n.exports = function(r, n) {
                var u = i[r + "Prototype"]
                  , a = u && u[n];
                if (a)
                    return a;
                var c = o[r]
                  , s = c && c.prototype;
                return s && s[n]
            }
        }
    })
      , tR = u({
        "node_modules/core-js-pure/es/array/virtual/filter.js": function(r, n) {
            tA(),
            n.exports = tI()("Array", "filter")
        }
    })
      , tL = u({
        "node_modules/core-js-pure/es/instance/filter.js": function(r, n) {
            var o = T()
              , i = tR()
              , u = Array.prototype;
            n.exports = function(r) {
                var n = r.filter;
                return r === u || o(u, r) && n === u.filter ? i : n
            }
        }
    })
      , tM = u({
        "node_modules/core-js-pure/stable/instance/filter.js": function(r, n) {
            n.exports = tL()
        }
    })
      , tN = u({
        "node_modules/core-js-pure/modules/es.object.get-own-property-descriptor.js": function() {
            var r = et()
              , n = c()
              , o = x()
              , i = W().f
              , u = h();
            r({
                target: "Object",
                stat: !0,
                forced: !u || n(function() {
                    i(1)
                }),
                sham: !u
            }, {
                getOwnPropertyDescriptor: function(r, n) {
                    return i(o(r), n)
                }
            })
        }
    })
      , tD = u({
        "node_modules/core-js-pure/es/object/get-own-property-descriptor.js": function(r, n) {
            tN();
            var o = E().Object
              , i = n.exports = function(r, n) {
                return o.getOwnPropertyDescriptor(r, n)
            }
            ;
            o.getOwnPropertyDescriptor.sham && (i.sham = !0)
        }
    })
      , tB = u({
        "node_modules/core-js-pure/stable/object/get-own-property-descriptor.js": function(r, n) {
            n.exports = tD()
        }
    })
      , tU = u({
        "node_modules/core-js-pure/internals/own-keys.js": function(r, n) {
            var o = O()
              , i = f()
              , u = eP()
              , a = eI()
              , c = $()
              , s = i([].concat);
            n.exports = o("Reflect", "ownKeys") || function(r) {
                var n = u.f(c(r))
                  , o = a.f;
                return o ? s(n, o(r)) : n
            }
        }
    })
      , tF = u({
        "node_modules/core-js-pure/modules/es.object.get-own-property-descriptors.js": function() {
            var r = et()
              , n = h()
              , o = tU()
              , i = x()
              , u = W()
              , a = ec();
            r({
                target: "Object",
                stat: !0,
                sham: !n
            }, {
                getOwnPropertyDescriptors: function(r) {
                    for (var n, c, s = i(r), l = u.f, f = o(s), d = {}, p = 0; f.length > p; )
                        void 0 !== (c = l(s, n = f[p++])) && a(d, n, c);
                    return d
                }
            })
        }
    })
      , tq = u({
        "node_modules/core-js-pure/es/object/get-own-property-descriptors.js": function(r, n) {
            tF(),
            n.exports = E().Object.getOwnPropertyDescriptors
        }
    })
      , tH = u({
        "node_modules/core-js-pure/stable/object/get-own-property-descriptors.js": function(r, n) {
            n.exports = tq()
        }
    })
      , tz = u({
        "node_modules/core-js-pure/modules/es.date.to-primitive.js": function() {}
    })
      , tV = u({
        "node_modules/core-js-pure/es/symbol/to-primitive.js": function(r, n) {
            tz(),
            e7(),
            n.exports = eM().f("toPrimitive")
        }
    })
      , tG = u({
        "node_modules/core-js-pure/stable/symbol/to-primitive.js": function(r, n) {
            n.exports = tV()
        }
    })
      , tJ = u({
        "node_modules/core-js-pure/internals/function-bind.js": function(r, o) {
            var i = f()
              , u = R()
              , a = _()
              , c = q()
              , l = eC()
              , d = s()
              , p = Function
              , v = i([].concat)
              , h = i([].join)
              , y = {};
            o.exports = d ? p.bind : function(r) {
                var o = u(this)
                  , i = o.prototype
                  , s = l(arguments, 1)
                  , f = function() {
                    var i = v(s, l(arguments));
                    return n(this, f) ? function(r, n, o) {
                        if (!c(y, n)) {
                            for (var i = [], u = 0; u < n; u++)
                                i[u] = "a[" + u + "]";
                            y[n] = p("C,a", "return new C(" + h(i, ",") + ")")
                        }
                        return y[n](r, o)
                    }(o, i.length, i) : o.apply(r, i)
                };
                return a(i) && (f.prototype = i),
                f
            }
        }
    })
      , tK = u({
        "node_modules/core-js-pure/internals/a-constructor.js": function(r, n) {
            var o = ed()
              , i = I()
              , u = TypeError;
            n.exports = function(r) {
                if (o(r))
                    return r;
                throw new u(i(r) + " is not a constructor")
            }
        }
    })
      , tW = u({
        "node_modules/core-js-pure/modules/es.reflect.construct.js": function() {
            var r = et()
              , o = O()
              , i = l()
              , u = tJ()
              , a = tK()
              , s = $()
              , f = _()
              , d = eS()
              , p = c()
              , v = o("Reflect", "construct")
              , h = Object.prototype
              , y = [].push
              , m = p(function() {
                function r() {}
                return !n(v(function() {}, [], r), r)
            })
              , g = !p(function() {
                v(function() {})
            })
              , b = m || g;
            r({
                target: "Reflect",
                stat: !0,
                forced: b,
                sham: b
            }, {
                construct: function(r, n) {
                    a(r),
                    s(n);
                    var o = arguments.length < 3 ? r : a(arguments[2]);
                    if (g && !m)
                        return v(r, n, o);
                    if (r === o) {
                        switch (n.length) {
                        case 0:
                            return new r;
                        case 1:
                            return new r(n[0]);
                        case 2:
                            return new r(n[0],n[1]);
                        case 3:
                            return new r(n[0],n[1],n[2]);
                        case 4:
                            return new r(n[0],n[1],n[2],n[3])
                        }
                        var c = [null];
                        return i(y, c, n),
                        new (i(u, r, c))
                    }
                    var l = o.prototype
                      , p = d(f(l) ? l : h)
                      , b = i(r, p, n);
                    return f(b) ? b : p
                }
            })
        }
    })
      , tY = u({
        "node_modules/core-js-pure/es/reflect/construct.js": function(r, n) {
            tW(),
            n.exports = E().Reflect.construct
        }
    })
      , tX = u({
        "node_modules/core-js-pure/stable/reflect/construct.js": function(r, n) {
            n.exports = tY()
        }
    })
      , tQ = u({
        "node_modules/core-js-pure/es/array/virtual/concat.js": function(r, n) {
            ey(),
            n.exports = tI()("Array", "concat")
        }
    })
      , t$ = u({
        "node_modules/core-js-pure/es/instance/concat.js": function(r, n) {
            var o = T()
              , i = tQ()
              , u = Array.prototype;
            n.exports = function(r) {
                var n = r.concat;
                return r === u || o(u, r) && n === u.concat ? i : n
            }
        }
    })
      , tZ = u({
        "node_modules/core-js-pure/stable/instance/concat.js": function(r, n) {
            n.exports = t$()
        }
    })
      , t0 = u({
        "node_modules/core-js-pure/modules/es.object.get-prototype-of.js": function() {
            var r = et()
              , n = c()
              , o = F()
              , i = ts()
              , u = tc();
            r({
                target: "Object",
                stat: !0,
                forced: n(function() {
                    i(1)
                }),
                sham: !u
            }, {
                getPrototypeOf: function(r) {
                    return i(o(r))
                }
            })
        }
    })
      , t1 = u({
        "node_modules/core-js-pure/es/object/get-prototype-of.js": function(r, n) {
            t0(),
            n.exports = E().Object.getPrototypeOf
        }
    })
      , t2 = u({
        "node_modules/core-js-pure/stable/object/get-prototype-of.js": function(r, n) {
            n.exports = t1()
        }
    })
      , t5 = u({
        "node_modules/core-js-pure/internals/string-repeat.js": function(r, n) {
            var o = eo()
              , i = eg()
              , u = w()
              , a = RangeError;
            n.exports = function(r) {
                var n = i(u(this))
                  , c = ""
                  , s = o(r);
                if (s < 0 || s === 1 / 0)
                    throw new a("Wrong number of repetitions");
                for (; s > 0; (s >>>= 1) && (n += n))
                    1 & s && (c += n);
                return c
            }
        }
    })
      , t3 = u({
        "node_modules/core-js-pure/internals/string-pad.js": function(r, n) {
            var o = f()
              , i = ei()
              , u = eg()
              , a = t5()
              , c = w()
              , s = o(a)
              , l = o("".slice)
              , d = Math.ceil
              , p = function(r) {
                return function(n, o, a) {
                    var f, p, v = u(c(n)), h = i(o), y = v.length, m = void 0 === a ? " " : u(a);
                    return h <= y || "" === m ? v : ((p = s(m, d((f = h - y) / m.length))).length > f && (p = l(p, 0, f)),
                    r ? v + p : p + v)
                }
            };
            n.exports = {
                start: p(!1),
                end: p(!0)
            }
        }
    })
      , t6 = u({
        "node_modules/core-js-pure/internals/date-to-iso-string.js": function(r, n) {
            var o = f()
              , i = c()
              , u = t3().start
              , a = RangeError
              , s = isFinite
              , l = Math.abs
              , d = Date.prototype
              , p = d.toISOString
              , v = o(d.getTime)
              , h = o(d.getUTCDate)
              , y = o(d.getUTCFullYear)
              , m = o(d.getUTCHours)
              , g = o(d.getUTCMilliseconds)
              , b = o(d.getUTCMinutes)
              , j = o(d.getUTCMonth)
              , w = o(d.getUTCSeconds);
            n.exports = i(function() {
                return "0385-07-25T07:06:39.999Z" !== p.call(new Date(-0x2d79883d2001))
            }) || !i(function() {
                p.call(new Date(NaN))
            }) ? function() {
                if (!s(v(this)))
                    throw new a("Invalid time value");
                var r = y(this)
                  , n = g(this)
                  , o = r < 0 ? "-" : r > 9999 ? "+" : "";
                return o + u(l(r), o ? 6 : 4, 0) + "-" + u(j(this) + 1, 2, 0) + "-" + u(h(this), 2, 0) + "T" + u(m(this), 2, 0) + ":" + u(b(this), 2, 0) + ":" + u(w(this), 2, 0) + "." + u(n, 3, 0) + "Z"
            }
            : p
        }
    })
      , t4 = u({
        "node_modules/core-js-pure/modules/es.date.to-json.js": function() {
            var r = et()
              , n = y()
              , o = F()
              , i = V()
              , u = t6()
              , a = d();
            r({
                target: "Date",
                proto: !0,
                forced: c()(function() {
                    return null !== new Date(NaN).toJSON() || 1 !== n(Date.prototype.toJSON, {
                        toISOString: function() {
                            return 1
                        }
                    })
                })
            }, {
                toJSON: function(r) {
                    var c = o(this)
                      , s = i(c, "number");
                    return "number" != typeof s || isFinite(s) ? "toISOString"in c || "Date" !== a(c) ? c.toISOString() : n(u, c) : null
                }
            })
        }
    })
      , t8 = u({
        "node_modules/core-js-pure/es/json/stringify.js": function(r, n) {
            t4(),
            eW();
            var o = E()
              , i = l();
            o.JSON || (o.JSON = {
                stringify: JSON.stringify
            }),
            n.exports = function(r, n, u) {
                return i(o.JSON.stringify, null, arguments)
            }
        }
    })
      , t7 = u({
        "node_modules/core-js-pure/stable/json/stringify.js": function(r, n) {
            n.exports = t8()
        }
    })
      , t9 = u({
        "node_modules/core-js-pure/internals/copy-constructor-properties.js": function(r, n) {
            var o = q()
              , i = tU()
              , u = W()
              , a = Z();
            n.exports = function(r, n, c) {
                for (var s = i(n), l = a.f, f = u.f, d = 0; d < s.length; d++) {
                    var p = s[d];
                    o(r, p) || c && o(c, p) || l(r, p, f(n, p))
                }
            }
        }
    })
      , re = u({
        "node_modules/core-js-pure/internals/install-error-cause.js": function(r, n) {
            var o = _()
              , i = ee();
            n.exports = function(r, n) {
                o(n) && "cause"in n && i(r, "cause", n.cause)
            }
        }
    })
      , rt = u({
        "node_modules/core-js-pure/internals/error-stack-clear.js": function(r, n) {
            var o = f()
              , i = Error
              , u = o("".replace)
              , a = String(new i("zxcasd").stack)
              , c = /\n\s*at [^:]*:[^\n]*/
              , s = c.test(a);
            n.exports = function(r, n) {
                if (s && "string" == typeof r && !i.prepareStackTrace)
                    for (; n--; )
                        r = u(r, c, "");
                return r
            }
        }
    })
      , rr = u({
        "node_modules/core-js-pure/internals/error-stack-installable.js": function(r, n) {
            var o = c()
              , i = g();
            n.exports = !o(function() {
                var r = Error("a");
                return !("stack"in r) || (Object.defineProperty(r, "stack", i(1, 7)),
                7 !== r.stack)
            })
        }
    })
      , rn = u({
        "node_modules/core-js-pure/internals/error-stack-install.js": function(r, n) {
            var o = ee()
              , i = rt()
              , u = rr()
              , a = Error.captureStackTrace;
            n.exports = function(r, n, c, s) {
                u && (a ? a(r, n) : o(r, "stack", i(c, s)))
            }
        }
    })
      , ro = u({
        "node_modules/core-js-pure/internals/is-array-iterator-method.js": function(r, n) {
            var o = z()
              , i = tu()
              , u = o("iterator")
              , a = Array.prototype;
            n.exports = function(r) {
                return void 0 !== r && (i.Array === r || a[u] === r)
            }
        }
    })
      , ri = u({
        "node_modules/core-js-pure/internals/get-iterator-method.js": function(r, n) {
            var o = el()
              , i = L()
              , u = j()
              , a = tu()
              , c = z()("iterator");
            n.exports = function(r) {
                if (!u(r))
                    return i(r, c) || i(r, "@@iterator") || a[o(r)]
            }
        }
    })
      , ru = u({
        "node_modules/core-js-pure/internals/get-iterator.js": function(r, n) {
            var o = y()
              , i = R()
              , u = $()
              , a = I()
              , c = ri()
              , s = TypeError;
            n.exports = function(r, n) {
                var l = arguments.length < 2 ? c(r) : n;
                if (i(l))
                    return u(o(l, r));
                throw new s(a(r) + " is not iterable")
            }
        }
    })
      , ra = u({
        "node_modules/core-js-pure/internals/iterator-close.js": function(r, n) {
            var o = y()
              , i = $()
              , u = L();
            n.exports = function(r, n, a) {
                var c, s;
                i(r);
                try {
                    if (!(c = u(r, "return"))) {
                        if ("throw" === n)
                            throw a;
                        return a
                    }
                    c = o(c, r)
                } catch (r) {
                    s = !0,
                    c = r
                }
                if ("throw" === n)
                    throw a;
                if (s)
                    throw c;
                return i(c),
                a
            }
        }
    })
      , rc = u({
        "node_modules/core-js-pure/internals/iterate.js": function(r, n) {
            var o = X()
              , i = y()
              , u = $()
              , a = I()
              , c = ro()
              , s = eu()
              , l = T()
              , f = ru()
              , d = ri()
              , p = ra()
              , v = TypeError
              , h = function(r, n) {
                this.stopped = r,
                this.result = n
            }
              , m = h.prototype;
            n.exports = function(r, n, y) {
                var g, b, j, w, x, _, E, O = y && y.that, T = !(!y || !y.AS_ENTRIES), k = !(!y || !y.IS_RECORD), S = !(!y || !y.IS_ITERATOR), P = !(!y || !y.INTERRUPTED), C = o(n, O), A = function(r) {
                    return g && p(g, "normal", r),
                    new h(!0,r)
                }, I = function(r) {
                    return T ? (u(r),
                    P ? C(r[0], r[1], A) : C(r[0], r[1])) : P ? C(r, A) : C(r)
                };
                if (k)
                    g = r.iterator;
                else if (S)
                    g = r;
                else {
                    if (!(b = d(r)))
                        throw new v(a(r) + " is not iterable");
                    if (c(b)) {
                        for (j = 0,
                        w = s(r); w > j; j++)
                            if ((x = I(r[j])) && l(m, x))
                                return x;
                        return new h(!1)
                    }
                    g = f(r, b)
                }
                for (_ = k ? r.next : g.next; !(E = i(_, g)).done; ) {
                    try {
                        x = I(E.value)
                    } catch (r) {
                        p(g, "throw", r)
                    }
                    if ("object" == typeof x && x && l(m, x))
                        return x
                }
                return new h(!1)
            }
        }
    })
      , rs = u({
        "node_modules/core-js-pure/internals/normalize-string-argument.js": function(r, n) {
            var o = eg();
            n.exports = function(r, n) {
                return void 0 === r ? arguments.length < 2 ? "" : n : o(r)
            }
        }
    })
      , rl = u({
        "node_modules/core-js-pure/modules/es.aggregate-error.constructor.js": function() {
            var r = et()
              , n = T()
              , o = ts()
              , i = th()
              , u = t9()
              , a = eS()
              , c = ee()
              , s = g()
              , l = re()
              , f = rn()
              , d = rc()
              , p = rs()
              , v = z()("toStringTag")
              , h = Error
              , y = [].push
              , m = function(r, u) {
                var s, g = n(b, this);
                i ? s = i(new h, g ? o(this) : b) : c(s = g ? this : a(b), v, "Error"),
                void 0 !== u && c(s, "message", p(u)),
                f(s, m, s.stack, 1),
                arguments.length > 2 && l(s, arguments[2]);
                var j = [];
                return d(r, y, {
                    that: j
                }),
                c(s, "errors", j),
                s
            };
            i ? i(m, h) : u(m, h, {
                name: !0
            });
            var b = m.prototype = a(h.prototype, {
                constructor: s(1, m),
                message: s(1, ""),
                name: s(1, "AggregateError")
            });
            r({
                global: !0,
                constructor: !0,
                arity: 2
            }, {
                AggregateError: m
            })
        }
    })
      , rf = u({
        "node_modules/core-js-pure/modules/es.aggregate-error.js": function() {
            rl()
        }
    })
      , rd = u({
        "node_modules/core-js-pure/internals/environment.js": function(r, n) {
            var o = a()
              , i = k()
              , u = d()
              , c = function(r) {
                return i.slice(0, r.length) === r
            };
            n.exports = c("Bun/") ? "BUN" : c("Cloudflare-Workers") ? "CLOUDFLARE" : c("Deno/") ? "DENO" : c("Node.js/") ? "NODE" : o.Bun && "string" == typeof Bun.version ? "BUN" : o.Deno && "object" == typeof Deno.version ? "DENO" : "process" === u(o.process) ? "NODE" : o.window && o.document ? "BROWSER" : "REST"
        }
    })
      , rp = u({
        "node_modules/core-js-pure/internals/environment-is-node.js": function(r, n) {
            n.exports = "NODE" === rd()
        }
    })
      , rv = u({
        "node_modules/core-js-pure/internals/set-species.js": function(r, n) {
            var o = O()
              , i = eL()
              , u = z()
              , a = h()
              , c = u("species");
            n.exports = function(r) {
                var n = o(r);
                a && n && !n[c] && i(n, c, {
                    configurable: !0,
                    get: function() {
                        return this
                    }
                })
            }
        }
    })
      , rh = u({
        "node_modules/core-js-pure/internals/an-instance.js": function(r, n) {
            var o = T()
              , i = TypeError;
            n.exports = function(r, n) {
                if (o(n, r))
                    return r;
                throw new i("Incorrect invocation")
            }
        }
    })
      , ry = u({
        "node_modules/core-js-pure/internals/species-constructor.js": function(r, n) {
            var o = $()
              , i = tK()
              , u = j()
              , a = z()("species");
            n.exports = function(r, n) {
                var c, s = o(r).constructor;
                return void 0 === s || u(c = o(s)[a]) ? n : i(c)
            }
        }
    })
      , rm = u({
        "node_modules/core-js-pure/internals/validate-arguments-length.js": function(r, n) {
            var o = TypeError;
            n.exports = function(r, n) {
                if (r < n)
                    throw new o("Not enough arguments");
                return r
            }
        }
    })
      , rg = u({
        "node_modules/core-js-pure/internals/environment-is-ios.js": function(r, n) {
            var o = k();
            n.exports = /(?:ipad|iphone|ipod).*applewebkit/i.test(o)
        }
    })
      , rb = u({
        "node_modules/core-js-pure/internals/task.js": function(r, n) {
            var o, i, u, s, f = a(), d = l(), p = X(), h = v(), y = q(), m = c(), g = eT(), b = eC(), j = J(), w = rm(), x = rg(), _ = rp(), E = f.setImmediate, O = f.clearImmediate, T = f.process, k = f.Dispatch, S = f.Function, P = f.MessageChannel, C = f.String, A = 0, I = {}, R = "onreadystatechange";
            m(function() {
                o = f.location
            });
            var L = function(r) {
                if (y(I, r)) {
                    var n = I[r];
                    delete I[r],
                    n()
                }
            }
              , M = function(r) {
                return function() {
                    L(r)
                }
            }
              , N = function(r) {
                L(r.data)
            }
              , D = function(r) {
                f.postMessage(C(r), o.protocol + "//" + o.host)
            };
            E && O || (E = function(r) {
                w(arguments.length, 1);
                var n = h(r) ? r : S(r)
                  , o = b(arguments, 1);
                return I[++A] = function() {
                    d(n, void 0, o)
                }
                ,
                i(A),
                A
            }
            ,
            O = function(r) {
                delete I[r]
            }
            ,
            _ ? i = function(r) {
                T.nextTick(M(r))
            }
            : k && k.now ? i = function(r) {
                k.now(M(r))
            }
            : P && !x ? (s = (u = new P).port2,
            u.port1.onmessage = N,
            i = p(s.postMessage, s)) : f.addEventListener && h(f.postMessage) && !f.importScripts && o && "file:" !== o.protocol && !m(D) ? (i = D,
            f.addEventListener("message", N, !1)) : i = R in j("script") ? function(r) {
                g.appendChild(j("script"))[R] = function() {
                    g.removeChild(this),
                    L(r)
                }
            }
            : function(r) {
                setTimeout(M(r), 0)
            }
            ),
            n.exports = {
                set: E,
                clear: O
            }
        }
    })
      , rj = u({
        "node_modules/core-js-pure/internals/safe-get-built-in.js": function(r, n) {
            var o = a()
              , i = h()
              , u = Object.getOwnPropertyDescriptor;
            n.exports = function(r) {
                if (!i)
                    return o[r];
                var n = u(o, r);
                return n && n.value
            }
        }
    })
      , rw = u({
        "node_modules/core-js-pure/internals/queue.js": function(r, n) {
            var o = function() {
                this.head = null,
                this.tail = null
            };
            o.prototype = {
                add: function(r) {
                    var n = {
                        item: r,
                        next: null
                    }
                      , o = this.tail;
                    o ? o.next = n : this.head = n,
                    this.tail = n
                },
                get: function() {
                    var r = this.head;
                    if (r)
                        return null === (this.head = r.next) && (this.tail = null),
                        r.item
                }
            },
            n.exports = o
        }
    })
      , rx = u({
        "node_modules/core-js-pure/internals/environment-is-ios-pebble.js": function(r, n) {
            var o = k();
            n.exports = /ipad|iphone|ipod/i.test(o) && "undefined" != typeof Pebble
        }
    })
      , r_ = u({
        "node_modules/core-js-pure/internals/environment-is-webos-webkit.js": function(r, n) {
            var o = k();
            n.exports = /web0s(?!.*chrome)/i.test(o)
        }
    })
      , rE = u({
        "node_modules/core-js-pure/internals/microtask.js": function(r, n) {
            var o, i, u, c, s, l, f, d = a(), p = rj(), v = X(), h = rb().set, y = rw(), m = rg(), g = rx(), b = r_(), j = rp(), w = d.MutationObserver || d.WebKitMutationObserver, x = d.document, _ = d.process, E = d.Promise, O = p("queueMicrotask");
            O || (l = new y,
            f = function() {
                var r, n;
                for (j && (r = _.domain) && r.exit(); n = l.get(); )
                    try {
                        n()
                    } catch (r) {
                        throw l.head && o(),
                        r
                    }
                r && r.enter()
            }
            ,
            m || j || b || !w || !x ? !g && E && E.resolve ? ((c = E.resolve(void 0)).constructor = E,
            s = v(c.then, c),
            o = function() {
                s(f)
            }
            ) : j ? o = function() {
                _.nextTick(f)
            }
            : (h = v(h, d),
            o = function() {
                h(f)
            }
            ) : (i = !0,
            u = x.createTextNode(""),
            new w(f).observe(u, {
                characterData: !0
            }),
            o = function() {
                u.data = i = !i
            }
            ),
            O = function(r) {
                l.head || o(),
                l.add(r)
            }
            ),
            n.exports = O
        }
    })
      , rO = u({
        "node_modules/core-js-pure/internals/host-report-errors.js": function(r, n) {
            n.exports = function(r, n) {}
        }
    })
      , rT = u({
        "node_modules/core-js-pure/internals/perform.js": function(r, n) {
            n.exports = function(r) {
                try {
                    return {
                        error: !1,
                        value: r()
                    }
                } catch (r) {
                    return {
                        error: !0,
                        value: r
                    }
                }
            }
        }
    })
      , rk = u({
        "node_modules/core-js-pure/internals/promise-native-constructor.js": function(r, n) {
            n.exports = a().Promise
        }
    })
      , rS = u({
        "node_modules/core-js-pure/internals/promise-constructor-detection.js": function(r, o) {
            var i = a()
              , u = rk()
              , c = v()
              , s = Y()
              , l = ef()
              , f = z()
              , d = rd()
              , p = N()
              , h = S()
              , y = u && u.prototype
              , m = f("species")
              , g = !1
              , b = c(i.PromiseRejectionEvent);
            o.exports = {
                CONSTRUCTOR: s("Promise", function() {
                    var r = l(u)
                      , o = r !== String(u);
                    if (!o && 66 === h || p && (!y.catch || !y.finally))
                        return !0;
                    if (!h || h < 51 || !/native code/.test(r)) {
                        var i = new u(function(r) {
                            r(1)
                        }
                        )
                          , a = function(r) {
                            r(function() {}, function() {})
                        };
                        if ((i.constructor = {})[m] = a,
                        !(g = n(i.then(function() {}), a)))
                            return !0
                    }
                    return !o && ("BROWSER" === d || "DENO" === d) && !b
                }),
                REJECTION_EVENT: b,
                SUBCLASSING: g
            }
        }
    })
      , rP = u({
        "node_modules/core-js-pure/internals/new-promise-capability.js": function(r, n) {
            var o = R()
              , i = TypeError
              , u = function(r) {
                var n, u;
                this.promise = new r(function(r, o) {
                    if (void 0 !== n || void 0 !== u)
                        throw new i("Bad Promise constructor");
                    n = r,
                    u = o
                }
                ),
                this.resolve = o(n),
                this.reject = o(u)
            };
            n.exports.f = function(r) {
                return new u(r)
            }
        }
    })
      , rC = u({
        "node_modules/core-js-pure/modules/es.promise.constructor.js": function() {
            var r, n, o, i = et(), u = N(), c = rp(), s = a(), l = y(), f = eR(), d = th(), p = eU(), h = rv(), m = R(), g = v(), b = _(), j = rh(), w = ry(), x = rb().set, E = rE(), O = rO(), T = rT(), k = rw(), S = eq(), P = rk(), C = rS(), A = rP(), I = "Promise", L = C.CONSTRUCTOR, M = C.REJECTION_EVENT, D = C.SUBCLASSING, B = S.getterFor(I), U = S.set, F = P && P.prototype, q = P, H = F, z = s.TypeError, V = s.document, G = s.process, J = A.f, K = J, W = !!(V && V.createEvent && s.dispatchEvent), Y = "unhandledrejection", X = function(r) {
                var n;
                return !(!b(r) || !g(n = r.then)) && n
            }, Q = function(r, n) {
                var o, i, u, a = n.value, c = 1 === n.state, s = c ? r.ok : r.fail, f = r.resolve, d = r.reject, p = r.domain;
                try {
                    s ? (c || (2 === n.rejection && en(n),
                    n.rejection = 1),
                    !0 === s ? o = a : (p && p.enter(),
                    o = s(a),
                    p && (p.exit(),
                    u = !0)),
                    o === r.promise ? d(new z("Promise-chain cycle")) : (i = X(o)) ? l(i, o, f, d) : f(o)) : d(a)
                } catch (r) {
                    p && !u && p.exit(),
                    d(r)
                }
            }, $ = function(r, n) {
                r.notified || (r.notified = !0,
                E(function() {
                    for (var o, i = r.reactions; o = i.get(); )
                        Q(o, r);
                    r.notified = !1,
                    n && !r.rejection && ee(r)
                }))
            }, Z = function(r, n, o) {
                var i, u;
                W ? ((i = V.createEvent("Event")).promise = n,
                i.reason = o,
                i.initEvent(r, !1, !0),
                s.dispatchEvent(i)) : i = {
                    promise: n,
                    reason: o
                },
                !M && (u = s["on" + r]) ? u(i) : r === Y && O("Unhandled promise rejection", o)
            }, ee = function(r) {
                l(x, s, function() {
                    var n, o = r.facade, i = r.value;
                    if (er(r) && (n = T(function() {
                        c ? G.emit("unhandledRejection", i, o) : Z(Y, o, i)
                    }),
                    r.rejection = c || er(r) ? 2 : 1,
                    n.error))
                        throw n.value
                })
            }, er = function(r) {
                return 1 !== r.rejection && !r.parent
            }, en = function(r) {
                l(x, s, function() {
                    var n = r.facade;
                    c ? G.emit("rejectionHandled", n) : Z("rejectionhandled", n, r.value)
                })
            }, eo = function(r, n, o) {
                return function(i) {
                    r(n, i, o)
                }
            }, ei = function(r, n, o) {
                r.done || (r.done = !0,
                o && (r = o),
                r.value = n,
                r.state = 2,
                $(r, !0))
            }, eu = function(r, n, o) {
                if (!r.done) {
                    r.done = !0,
                    o && (r = o);
                    try {
                        if (r.facade === n)
                            throw new z("Promise can't be resolved itself");
                        var i = X(n);
                        i ? E(function() {
                            var o = {
                                done: !1
                            };
                            try {
                                l(i, n, eo(eu, o, r), eo(ei, o, r))
                            } catch (n) {
                                ei(o, n, r)
                            }
                        }) : (r.value = n,
                        r.state = 1,
                        $(r, !1))
                    } catch (n) {
                        ei({
                            done: !1
                        }, n, r)
                    }
                }
            };
            if (L && (H = (q = function(n) {
                j(this, H),
                m(n),
                l(r, this);
                var o = B(this);
                try {
                    n(eo(eu, o), eo(ei, o))
                } catch (r) {
                    ei(o, r)
                }
            }
            ).prototype,
            (r = function(r) {
                U(this, {
                    type: I,
                    done: !1,
                    notified: !1,
                    parent: !1,
                    reactions: new k,
                    rejection: !1,
                    state: 0,
                    value: null
                })
            }
            ).prototype = f(H, "then", function(r, n) {
                var o = B(this)
                  , i = J(w(this, q));
                return o.parent = !0,
                i.ok = !g(r) || r,
                i.fail = g(n) && n,
                i.domain = c ? G.domain : void 0,
                0 === o.state ? o.reactions.add(i) : E(function() {
                    Q(i, o)
                }),
                i.promise
            }),
            n = function() {
                var n = new r
                  , o = B(n);
                this.promise = n,
                this.resolve = eo(eu, o),
                this.reject = eo(ei, o)
            }
            ,
            A.f = J = function(r) {
                return r === q || void 0 === r ? new n(r) : K(r)
            }
            ,
            !u && g(P) && F !== Object.prototype)) {
                o = F.then,
                D || f(F, "then", function(r, n) {
                    var i = this;
                    return new q(function(r, n) {
                        l(o, i, r, n)
                    }
                    ).then(r, n)
                }, {
                    unsafe: !0
                });
                try {
                    delete F.constructor
                } catch (r) {}
                d && d(F, H)
            }
            i({
                global: !0,
                constructor: !0,
                wrap: !0,
                forced: L
            }, {
                Promise: q
            }),
            p(q, I, !1, !0),
            h(I)
        }
    })
      , rA = u({
        "node_modules/core-js-pure/internals/check-correctness-of-iteration.js": function(r, n) {
            var o, i, u = z()("iterator"), a = !1;
            try {
                o = 0,
                (i = {
                    next: function() {
                        return {
                            done: !!o++
                        }
                    },
                    return: function() {
                        a = !0
                    }
                })[u] = function() {
                    return this
                }
                ,
                Array.from(i, function() {
                    throw 2
                })
            } catch (r) {}
            n.exports = function(r, n) {
                try {
                    if (!n && !a)
                        return !1
                } catch (r) {
                    return !1
                }
                var o = !1;
                try {
                    var i = {};
                    i[u] = function() {
                        return {
                            next: function() {
                                return {
                                    done: o = !0
                                }
                            }
                        }
                    }
                    ,
                    r(i)
                } catch (r) {}
                return o
            }
        }
    })
      , rI = u({
        "node_modules/core-js-pure/internals/promise-statics-incorrect-iteration.js": function(r, n) {
            var o = rk()
              , i = rA();
            n.exports = rS().CONSTRUCTOR || !i(function(r) {
                o.all(r).then(void 0, function() {})
            })
        }
    })
      , rR = u({
        "node_modules/core-js-pure/modules/es.promise.all.js": function() {
            var r = et()
              , n = y()
              , o = R()
              , i = rP()
              , u = rT()
              , a = rc();
            r({
                target: "Promise",
                stat: !0,
                forced: rI()
            }, {
                all: function(r) {
                    var c = this
                      , s = i.f(c)
                      , l = s.resolve
                      , f = s.reject
                      , d = u(function() {
                        var i = o(c.resolve)
                          , u = []
                          , s = 0
                          , d = 1;
                        a(r, function(r) {
                            var o = s++
                              , a = !1;
                            d++,
                            n(i, c, r).then(function(r) {
                                a || (a = !0,
                                u[o] = r,
                                --d || l(u))
                            }, f)
                        }),
                        --d || l(u)
                    });
                    return d.error && f(d.value),
                    s.promise
                }
            })
        }
    })
      , rL = u({
        "node_modules/core-js-pure/modules/es.promise.catch.js": function() {
            var r, n = et(), o = N(), i = rS().CONSTRUCTOR, u = rk(), a = O(), c = v(), s = eR(), l = u && u.prototype;
            n({
                target: "Promise",
                proto: !0,
                forced: i,
                real: !0
            }, {
                catch: function(r) {
                    return this.then(void 0, r)
                }
            }),
            !o && c(u) && (r = a("Promise").prototype.catch,
            l.catch !== r && s(l, "catch", r, {
                unsafe: !0
            }))
        }
    })
      , rM = u({
        "node_modules/core-js-pure/modules/es.promise.race.js": function() {
            var r = et()
              , n = y()
              , o = R()
              , i = rP()
              , u = rT()
              , a = rc();
            r({
                target: "Promise",
                stat: !0,
                forced: rI()
            }, {
                race: function(r) {
                    var c = this
                      , s = i.f(c)
                      , l = s.reject
                      , f = u(function() {
                        var i = o(c.resolve);
                        a(r, function(r) {
                            n(i, c, r).then(s.resolve, l)
                        })
                    });
                    return f.error && l(f.value),
                    s.promise
                }
            })
        }
    })
      , rN = u({
        "node_modules/core-js-pure/modules/es.promise.reject.js": function() {
            var r = et()
              , n = rP();
            r({
                target: "Promise",
                stat: !0,
                forced: rS().CONSTRUCTOR
            }, {
                reject: function(r) {
                    var o = n.f(this);
                    return (0,
                    o.reject)(r),
                    o.promise
                }
            })
        }
    })
      , rD = u({
        "node_modules/core-js-pure/internals/promise-resolve.js": function(r, n) {
            var o = $()
              , i = _()
              , u = rP();
            n.exports = function(r, n) {
                if (o(r),
                i(n) && n.constructor === r)
                    return n;
                var a = u.f(r);
                return (0,
                a.resolve)(n),
                a.promise
            }
        }
    })
      , rB = u({
        "node_modules/core-js-pure/modules/es.promise.resolve.js": function() {
            var r = et()
              , n = O()
              , o = N()
              , i = rk()
              , u = rS().CONSTRUCTOR
              , a = rD()
              , c = n("Promise")
              , s = o && !u;
            r({
                target: "Promise",
                stat: !0,
                forced: o || u
            }, {
                resolve: function(r) {
                    return a(s && this === c ? i : this, r)
                }
            })
        }
    })
      , rU = u({
        "node_modules/core-js-pure/modules/es.promise.js": function() {
            rC(),
            rR(),
            rL(),
            rM(),
            rN(),
            rB()
        }
    })
      , rF = u({
        "node_modules/core-js-pure/modules/es.promise.all-settled.js": function() {
            var r = et()
              , n = y()
              , o = R()
              , i = rP()
              , u = rT()
              , a = rc();
            r({
                target: "Promise",
                stat: !0,
                forced: rI()
            }, {
                allSettled: function(r) {
                    var c = this
                      , s = i.f(c)
                      , l = s.resolve
                      , f = s.reject
                      , d = u(function() {
                        var i = o(c.resolve)
                          , u = []
                          , s = 0
                          , f = 1;
                        a(r, function(r) {
                            var o = s++
                              , a = !1;
                            f++,
                            n(i, c, r).then(function(r) {
                                a || (a = !0,
                                u[o] = {
                                    status: "fulfilled",
                                    value: r
                                },
                                --f || l(u))
                            }, function(r) {
                                a || (a = !0,
                                u[o] = {
                                    status: "rejected",
                                    reason: r
                                },
                                --f || l(u))
                            })
                        }),
                        --f || l(u)
                    });
                    return d.error && f(d.value),
                    s.promise
                }
            })
        }
    })
      , rq = u({
        "node_modules/core-js-pure/modules/es.promise.any.js": function() {
            var r = et()
              , n = y()
              , o = R()
              , i = O()
              , u = rP()
              , a = rT()
              , c = rc()
              , s = rI()
              , l = "No one promise resolved";
            r({
                target: "Promise",
                stat: !0,
                forced: s
            }, {
                any: function(r) {
                    var s = this
                      , f = i("AggregateError")
                      , d = u.f(s)
                      , p = d.resolve
                      , v = d.reject
                      , h = a(function() {
                        var i = o(s.resolve)
                          , u = []
                          , a = 0
                          , d = 1
                          , h = !1;
                        c(r, function(r) {
                            var o = a++
                              , c = !1;
                            d++,
                            n(i, s, r).then(function(r) {
                                c || h || (h = !0,
                                p(r))
                            }, function(r) {
                                c || h || (c = !0,
                                u[o] = r,
                                --d || v(new f(u,l)))
                            })
                        }),
                        --d || v(new f(u,l))
                    });
                    return h.error && v(h.value),
                    d.promise
                }
            })
        }
    })
      , rH = u({
        "node_modules/core-js-pure/modules/es.promise.with-resolvers.js": function() {
            var r = et()
              , n = rP();
            r({
                target: "Promise",
                stat: !0
            }, {
                withResolvers: function() {
                    var r = n.f(this);
                    return {
                        promise: r.promise,
                        resolve: r.resolve,
                        reject: r.reject
                    }
                }
            })
        }
    })
      , rz = u({
        "node_modules/core-js-pure/modules/es.promise.finally.js": function() {
            var r, n = et(), o = N(), i = rk(), u = c(), a = O(), s = v(), l = ry(), f = rD(), d = eR(), p = i && i.prototype;
            n({
                target: "Promise",
                proto: !0,
                real: !0,
                forced: !!i && u(function() {
                    p.finally.call({
                        then: function() {}
                    }, function() {})
                })
            }, {
                finally: function(r) {
                    var n = l(this, a("Promise"))
                      , o = s(r);
                    return this.then(o ? function(o) {
                        return f(n, r()).then(function() {
                            return o
                        })
                    }
                    : r, o ? function(o) {
                        return f(n, r()).then(function() {
                            throw o
                        })
                    }
                    : r)
                }
            }),
            !o && s(i) && (r = a("Promise").prototype.finally,
            p.finally !== r && d(p, "finally", r, {
                unsafe: !0
            }))
        }
    })
      , rV = u({
        "node_modules/core-js-pure/es/promise/index.js": function(r, n) {
            rf(),
            tg(),
            em(),
            rU(),
            rF(),
            rq(),
            rH(),
            rz(),
            t_(),
            n.exports = E().Promise
        }
    })
      , rG = u({
        "node_modules/core-js-pure/stable/promise/index.js": function(r, n) {
            var o = rV();
            tj(),
            n.exports = o
        }
    })
      , rJ = u({
        "node_modules/@liepin/js-appbridge-sdk/src/common/config.ts": function(r) {
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.default = void 0,
            r.default = {
                debug: !1
            }
        }
    })
      , rK = u({
        "node_modules/@liepin/js-appbridge-sdk/src/common/log.ts": function(r) {
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.log = function(r) {
                o.default.debug
            }
            ,
            r.logError = function(r) {
                var n;
                o.default.debug,
                null === (n = o.default.errorLog) || void 0 === n || n.call(o.default, r)
            }
            ;
            var n, o = (n = rJ()) && n.__esModule ? n : {
                default: n
            }
        }
    })
      , rW = u({
        "node_modules/@liepin/js-appbridge-sdk/src/common/callNative.ts": function(r) {
            var n, o = t7(), i = rG();
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.callNative = l,
            r.callNativePromise = function(r) {
                return new i(function(n, i) {
                    l({
                        plugin: r.plugin,
                        action: r.action,
                        params: r.params,
                        success: n,
                        progress: r.progress,
                        error: function(r, n) {
                            i(Error(r, {
                                cause: o(n)
                            }))
                        }
                    })
                }
                )
            }
            ,
            r.handleResponseFromNative = function(r) {
                var n, o = JSON.parse(r);
                (0,
                u.log)("调用native后的响应, ".concat(r));
                var i = o.status
                  , s = o.callbackId
                  , l = o.data
                  , f = o.msg
                  , d = o.complete;
                if (s) {
                    var p, v, h, y = function() {
                        return delete c[s]
                    }, m = c[s];
                    if (!m)
                        return void (0,
                        u.logError)("native回调js失败，回调id：".concat(s));
                    switch (i) {
                    case a.success:
                        !0 === d ? (null === (p = m.success) || void 0 === p || p.call(m, l, o),
                        y()) : null === (v = m.progress) || void 0 === v || v.call(m, l, o);
                        break;
                    case a.canceled:
                        navigator.userAgent.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/) && (null === (h = m.error) || void 0 === h || h.call(m, f, o)),
                        y();
                        break;
                    case a.error:
                    case a.abnormal:
                    case a.noRegistered:
                        null === (n = m.error) || void 0 === n || n.call(m, f, o),
                        y();
                        break;
                    default:
                        y()
                    }
                }
            }
            ;
            var u = rK()
              , a = ((n = a || {}).success = "0",
            n.error = "-1",
            n.abnormal = "1",
            n.noRegistered = "-2",
            n.canceled = "7",
            n)
              , c = {};
            function s() {
                return Math.random().toString(36).substring(4) + Date.now().toString(36) + String(++s.id)
            }
            function l(r) {
                var n, i = r.plugin, a = r.action, l = r.params, f = r.success, d = r.error, p = r.progress;
                (f || d || p) && (c[n = s()] = {},
                f && (c[n].success = f),
                d && (c[n].error = d),
                p && (c[n].progress = p));
                var v = o({
                    plugin: i,
                    action: void 0 === a ? "" : a,
                    params: void 0 === l ? {} : l,
                    callbackId: n
                });
                (0,
                u.log)("调用native, ".concat(v)),
                window.XWebView._callNative(v)
            }
            s.id = 1
        }
    })
      , rY = u({
        "node_modules/core-js-pure/modules/es.array.map.js": function() {
            var r = et()
              , n = eH().map;
            r({
                target: "Array",
                proto: !0,
                forced: !eh()("map")
            }, {
                map: function(r) {
                    return n(this, r, arguments.length > 1 ? arguments[1] : void 0)
                }
            })
        }
    })
      , rX = u({
        "node_modules/core-js-pure/es/array/virtual/map.js": function(r, n) {
            rY(),
            n.exports = tI()("Array", "map")
        }
    })
      , rQ = u({
        "node_modules/core-js-pure/es/instance/map.js": function(r, n) {
            var o = T()
              , i = rX()
              , u = Array.prototype;
            n.exports = function(r) {
                var n = r.map;
                return r === u || o(u, r) && n === u.map ? i : n
            }
        }
    })
      , r$ = u({
        "node_modules/core-js-pure/stable/instance/map.js": function(r, n) {
            n.exports = rQ()
        }
    })
      , rZ = u({
        "node_modules/core-js-pure/modules/es.array.slice.js": function() {
            var r = et()
              , n = er()
              , o = ed()
              , i = _()
              , u = eb()
              , a = eu()
              , c = x()
              , s = ec()
              , l = z()
              , f = eh()
              , d = eC()
              , p = f("slice")
              , v = l("species")
              , h = Array
              , y = Math.max;
            r({
                target: "Array",
                proto: !0,
                forced: !p
            }, {
                slice: function(r, l) {
                    var f, p, m, g = c(this), b = a(g), j = u(r, b), w = u(void 0 === l ? b : l, b);
                    if (n(g) && ((o(f = g.constructor) && (f === h || n(f.prototype)) || i(f) && null === (f = f[v])) && (f = void 0),
                    f === h || void 0 === f))
                        return d(g, j, w);
                    for (p = new (void 0 === f ? h : f)(y(w - j, 0)),
                    m = 0; j < w; j++,
                    m++)
                        j in g && s(p, m, g[j]);
                    return p.length = m,
                    p
                }
            })
        }
    })
      , r0 = u({
        "node_modules/core-js-pure/es/array/virtual/slice.js": function(r, n) {
            rZ(),
            n.exports = tI()("Array", "slice")
        }
    })
      , r1 = u({
        "node_modules/core-js-pure/es/instance/slice.js": function(r, n) {
            var o = T()
              , i = r0()
              , u = Array.prototype;
            n.exports = function(r) {
                var n = r.slice;
                return r === u || o(u, r) && n === u.slice ? i : n
            }
        }
    })
      , r2 = u({
        "node_modules/core-js-pure/stable/instance/slice.js": function(r, n) {
            n.exports = r1()
        }
    })
      , r5 = u({
        "node_modules/core-js-pure/internals/call-with-safe-iteration-closing.js": function(r, n) {
            var o = $()
              , i = ra();
            n.exports = function(r, n, u, a) {
                try {
                    return a ? n(o(u)[0], u[1]) : n(u)
                } catch (n) {
                    i(r, "throw", n)
                }
            }
        }
    })
      , r3 = u({
        "node_modules/core-js-pure/internals/array-from.js": function(r, n) {
            var o = X()
              , i = y()
              , u = F()
              , a = r5()
              , c = ro()
              , s = ed()
              , l = eu()
              , f = ec()
              , d = ru()
              , p = ri()
              , v = Array;
            n.exports = function(r) {
                var n = u(r)
                  , h = s(this)
                  , y = arguments.length
                  , m = y > 1 ? arguments[1] : void 0
                  , g = void 0 !== m;
                g && (m = o(m, y > 2 ? arguments[2] : void 0));
                var b, j, w, x, _, E, O = p(n), T = 0;
                if (!O || this === v && c(O))
                    for (b = l(n),
                    j = h ? new this(b) : v(b); b > T; T++)
                        E = g ? m(n[T], T) : n[T],
                        f(j, T, E);
                else
                    for (j = h ? new this : [],
                    _ = (x = d(n, O)).next; !(w = i(_, x)).done; T++)
                        E = g ? a(x, m, [w.value, T], !0) : w.value,
                        f(j, T, E);
                return j.length = T,
                j
            }
        }
    })
      , r6 = u({
        "node_modules/core-js-pure/modules/es.array.from.js": function() {
            var r = et()
              , n = r3();
            r({
                target: "Array",
                stat: !0,
                forced: !rA()(function(r) {
                    Array.from(r)
                })
            }, {
                from: n
            })
        }
    })
      , r4 = u({
        "node_modules/core-js-pure/es/array/from.js": function(r, n) {
            t_(),
            r6(),
            n.exports = E().Array.from
        }
    })
      , r8 = u({
        "node_modules/core-js-pure/stable/array/from.js": function(r, n) {
            n.exports = r4()
        }
    })
      , r7 = u({
        "node_modules/core-js-pure/internals/array-set-length.js": function(r, o) {
            var i = h()
              , u = er()
              , a = TypeError
              , c = Object.getOwnPropertyDescriptor;
            o.exports = i && !function() {
                if (void 0 !== this)
                    return !0;
                try {
                    Object.defineProperty([], "length", {
                        writable: !1
                    }).length = 1
                } catch (r) {
                    return n(r, TypeError)
                }
            }() ? function(r, n) {
                if (u(r) && !c(r, "length").writable)
                    throw new a("Cannot set read only .length");
                return r.length = n
            }
            : function(r, n) {
                return r.length = n
            }
        }
    })
      , r9 = u({
        "node_modules/core-js-pure/internals/delete-property-or-throw.js": function(r, n) {
            var o = I()
              , i = TypeError;
            n.exports = function(r, n) {
                if (!delete r[n])
                    throw new i("Cannot delete property " + o(n) + " of " + o(r))
            }
        }
    })
      , ne = u({
        "node_modules/core-js-pure/modules/es.array.splice.js": function() {
            var r = et()
              , n = F()
              , o = eb()
              , i = eo()
              , u = eu()
              , a = r7()
              , c = ea()
              , s = ev()
              , l = ec()
              , f = r9()
              , d = eh()("splice")
              , p = Math.max
              , v = Math.min;
            r({
                target: "Array",
                proto: !0,
                forced: !d
            }, {
                splice: function(r, d) {
                    var h, y, m, g, b, j, w = n(this), x = u(w), _ = o(r, x), E = arguments.length;
                    for (0 === E ? h = y = 0 : 1 === E ? (h = 0,
                    y = x - _) : (h = E - 2,
                    y = v(p(i(d), 0), x - _)),
                    c(x + h - y),
                    m = s(w, y),
                    g = 0; g < y; g++)
                        (b = _ + g)in w && l(m, g, w[b]);
                    if (m.length = y,
                    h < y) {
                        for (g = _; g < x - y; g++)
                            j = g + h,
                            (b = g + y)in w ? w[j] = w[b] : f(w, j);
                        for (g = x; g > x - y + h; g--)
                            f(w, g - 1)
                    } else if (h > y)
                        for (g = x - y; g > _; g--)
                            j = g + h - 1,
                            (b = g + y - 1)in w ? w[j] = w[b] : f(w, j);
                    for (g = 0; g < h; g++)
                        w[g + _] = arguments[g + 2];
                    return a(w, x - y + h),
                    m
                }
            })
        }
    })
      , nt = u({
        "node_modules/core-js-pure/es/array/virtual/splice.js": function(r, n) {
            ne(),
            n.exports = tI()("Array", "splice")
        }
    })
      , nr = u({
        "node_modules/core-js-pure/es/instance/splice.js": function(r, n) {
            var o = T()
              , i = nt()
              , u = Array.prototype;
            n.exports = function(r) {
                var n = r.splice;
                return r === u || o(u, r) && n === u.splice ? i : n
            }
        }
    })
      , nn = u({
        "node_modules/core-js-pure/stable/instance/splice.js": function(r, n) {
            n.exports = nr()
        }
    })
      , no = u({
        "src/common/md5.ts": function(r) {
            var n = tZ();
            function o(r, n) {
                var o = (65535 & r) + (65535 & n);
                return (r >> 16) + (n >> 16) + (o >> 16) << 16 | 65535 & o
            }
            function i(r, n, i, u, a, c) {
                var s;
                return o((s = o(o(n, r), o(u, c))) << a | s >>> 32 - a, i)
            }
            function u(r, n, o, u, a, c, s) {
                return i(n & o | ~n & u, r, n, a, c, s)
            }
            function a(r, n, o, u, a, c, s) {
                return i(n & u | o & ~u, r, n, a, c, s)
            }
            function c(r, n, o, u, a, c, s) {
                return i(n ^ o ^ u, r, n, a, c, s)
            }
            function s(r, n, o, u, a, c, s) {
                return i(o ^ (n | ~u), r, n, a, c, s)
            }
            function l(r, n) {
                r[n >> 5] |= 128 << n % 32,
                r[14 + (n + 64 >>> 9 << 4)] = n;
                var i, l, f, d, p, v = 0x67452301, h = -0x10325477, y = -0x67452302, m = 0x10325476;
                for (i = 0; i < r.length; i += 16)
                    l = v,
                    f = h,
                    d = y,
                    p = m,
                    v = u(v, h, y, m, r[i], 7, -0x28955b88),
                    m = u(m, v, h, y, r[i + 1], 12, -0x173848aa),
                    y = u(y, m, v, h, r[i + 2], 17, 0x242070db),
                    h = u(h, y, m, v, r[i + 3], 22, -0x3e423112),
                    v = u(v, h, y, m, r[i + 4], 7, -0xa83f051),
                    m = u(m, v, h, y, r[i + 5], 12, 0x4787c62a),
                    y = u(y, m, v, h, r[i + 6], 17, -0x57cfb9ed),
                    h = u(h, y, m, v, r[i + 7], 22, -0x2b96aff),
                    v = u(v, h, y, m, r[i + 8], 7, 0x698098d8),
                    m = u(m, v, h, y, r[i + 9], 12, -0x74bb0851),
                    y = u(y, m, v, h, r[i + 10], 17, -42063),
                    h = u(h, y, m, v, r[i + 11], 22, -0x76a32842),
                    v = u(v, h, y, m, r[i + 12], 7, 0x6b901122),
                    m = u(m, v, h, y, r[i + 13], 12, -0x2678e6d),
                    y = u(y, m, v, h, r[i + 14], 17, -0x5986bc72),
                    v = a(v, h = u(h, y, m, v, r[i + 15], 22, 0x49b40821), y, m, r[i + 1], 5, -0x9e1da9e),
                    m = a(m, v, h, y, r[i + 6], 9, -0x3fbf4cc0),
                    y = a(y, m, v, h, r[i + 11], 14, 0x265e5a51),
                    h = a(h, y, m, v, r[i], 20, -0x16493856),
                    v = a(v, h, y, m, r[i + 5], 5, -0x29d0efa3),
                    m = a(m, v, h, y, r[i + 10], 9, 0x2441453),
                    y = a(y, m, v, h, r[i + 15], 14, -0x275e197f),
                    h = a(h, y, m, v, r[i + 4], 20, -0x182c0438),
                    v = a(v, h, y, m, r[i + 9], 5, 0x21e1cde6),
                    m = a(m, v, h, y, r[i + 14], 9, -0x3cc8f82a),
                    y = a(y, m, v, h, r[i + 3], 14, -0xb2af279),
                    h = a(h, y, m, v, r[i + 8], 20, 0x455a14ed),
                    v = a(v, h, y, m, r[i + 13], 5, -0x561c16fb),
                    m = a(m, v, h, y, r[i + 2], 9, -0x3105c08),
                    y = a(y, m, v, h, r[i + 7], 14, 0x676f02d9),
                    v = c(v, h = a(h, y, m, v, r[i + 12], 20, -0x72d5b376), y, m, r[i + 5], 4, -378558),
                    m = c(m, v, h, y, r[i + 8], 11, -0x788e097f),
                    y = c(y, m, v, h, r[i + 11], 16, 0x6d9d6122),
                    h = c(h, y, m, v, r[i + 14], 23, -0x21ac7f4),
                    v = c(v, h, y, m, r[i + 1], 4, -0x5b4115bc),
                    m = c(m, v, h, y, r[i + 4], 11, 0x4bdecfa9),
                    y = c(y, m, v, h, r[i + 7], 16, -0x944b4a0),
                    h = c(h, y, m, v, r[i + 10], 23, -0x41404390),
                    v = c(v, h, y, m, r[i + 13], 4, 0x289b7ec6),
                    m = c(m, v, h, y, r[i], 11, -0x155ed806),
                    y = c(y, m, v, h, r[i + 3], 16, -0x2b10cf7b),
                    h = c(h, y, m, v, r[i + 6], 23, 0x4881d05),
                    v = c(v, h, y, m, r[i + 9], 4, -0x262b2fc7),
                    m = c(m, v, h, y, r[i + 12], 11, -0x1924661b),
                    y = c(y, m, v, h, r[i + 15], 16, 0x1fa27cf8),
                    v = s(v, h = c(h, y, m, v, r[i + 2], 23, -0x3b53a99b), y, m, r[i], 6, -0xbd6ddbc),
                    m = s(m, v, h, y, r[i + 7], 10, 0x432aff97),
                    y = s(y, m, v, h, r[i + 14], 15, -0x546bdc59),
                    h = s(h, y, m, v, r[i + 5], 21, -0x36c5fc7),
                    v = s(v, h, y, m, r[i + 12], 6, 0x655b59c3),
                    m = s(m, v, h, y, r[i + 3], 10, -0x70f3336e),
                    y = s(y, m, v, h, r[i + 10], 15, -1051523),
                    h = s(h, y, m, v, r[i + 1], 21, -0x7a7ba22f),
                    v = s(v, h, y, m, r[i + 8], 6, 0x6fa87e4f),
                    m = s(m, v, h, y, r[i + 15], 10, -0x1d31920),
                    y = s(y, m, v, h, r[i + 6], 15, -0x5cfebcec),
                    h = s(h, y, m, v, r[i + 13], 21, 0x4e0811a1),
                    v = s(v, h, y, m, r[i + 4], 6, -0x8ac817e),
                    m = s(m, v, h, y, r[i + 11], 10, -0x42c50dcb),
                    y = s(y, m, v, h, r[i + 2], 15, 0x2ad7d2bb),
                    h = s(h, y, m, v, r[i + 9], 21, -0x14792c6f),
                    v = o(v, l),
                    h = o(h, f),
                    y = o(y, d),
                    m = o(m, p);
                return [v, h, y, m]
            }
            function f(r) {
                var n, o = "", i = 32 * r.length;
                for (n = 0; n < i; n += 8)
                    o += String.fromCharCode(r[n >> 5] >>> n % 32 & 255);
                return o
            }
            function d(r) {
                var n, o = [];
                for (o[(r.length >> 2) - 1] = void 0,
                n = 0; n < o.length; n += 1)
                    o[n] = 0;
                var i = 8 * r.length;
                for (n = 0; n < i; n += 8)
                    o[n >> 5] |= (255 & r.charCodeAt(n / 8)) << n % 32;
                return o
            }
            function p(r) {
                var n, o, i = "0123456789abcdef", u = "";
                for (o = 0; o < r.length; o += 1)
                    u += i.charAt((n = r.charCodeAt(o)) >>> 4 & 15) + i.charAt(15 & n);
                return u
            }
            function v(r) {
                return unescape(encodeURIComponent(r))
            }
            function h(r) {
                var n;
                return f(l(d(n = v(r)), 8 * n.length))
            }
            function y(r, o) {
                return function(r, o) {
                    var i, u, a = d(r), c = [], s = [];
                    for (c[15] = s[15] = void 0,
                    a.length > 16 && (a = l(a, 8 * r.length)),
                    i = 0; i < 16; i += 1)
                        c[i] = 0x36363636 ^ a[i],
                        s[i] = 0x5c5c5c5c ^ a[i];
                    return u = l(n(c).call(c, d(o)), 512 + 8 * o.length),
                    f(l(n(s).call(s, u), 640))
                }(v(r), v(o))
            }
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.default = void 0,
            r.default = function(r, n, o) {
                return n ? o ? y(n, r) : p(y(n, r)) : o ? h(r) : p(h(r))
            }
        }
    })
      , ni = u({
        "node_modules/core-js-pure/es/get-iterator-method.js": function(r, n) {
            tg(),
            t_(),
            n.exports = ri()
        }
    })
      , nu = u({
        "node_modules/core-js-pure/stable/get-iterator-method.js": function(r, n) {
            var o = ni();
            tj(),
            n.exports = o
        }
    })
      , na = u({
        "node_modules/core-js-pure/actual/get-iterator-method.js": function(r, n) {
            n.exports = nu()
        }
    })
      , nc = u({
        "node_modules/core-js-pure/full/get-iterator-method.js": function(r, n) {
            n.exports = na()
        }
    })
      , ns = u({
        "node_modules/core-js-pure/features/get-iterator-method.js": function(r, n) {
            n.exports = nc()
        }
    })
      , nl = u({
        "src/common/cookie.ts": function(r) {
            var n = tw()
              , o = ns()
              , i = r2()
              , u = r8()
              , a = tZ();
            function c(r, n) {
                (null == n || n > r.length) && (n = r.length);
                for (var o = 0, i = Array(n); o < n; o++)
                    i[o] = r[o];
                return i
            }
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.cookie = void 0,
            r.cookie = {
                get: function(r) {
                    var a, s = "".concat(r, "="), l = function(r, a) {
                        var s = void 0 !== n && o(r) || r["@@iterator"];
                        if (!s) {
                            if (Array.isArray(r) || (s = function(r, n) {
                                if (r) {
                                    if ("string" == typeof r)
                                        return c(r, void 0);
                                    var o, a = i(o = ({}).toString.call(r)).call(o, 8, -1);
                                    return "Object" === a && r.constructor && (a = r.constructor.name),
                                    "Map" === a || "Set" === a ? u(r) : "Arguments" === a || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(a) ? c(r, void 0) : void 0
                                }
                            }(r))) {
                                s && (r = s);
                                var l = 0
                                  , f = function() {};
                                return {
                                    s: f,
                                    n: function() {
                                        return l >= r.length ? {
                                            done: !0
                                        } : {
                                            done: !1,
                                            value: r[l++]
                                        }
                                    },
                                    e: function(r) {
                                        throw r
                                    },
                                    f: f
                                }
                            }
                            throw TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")
                        }
                        var d, p = !0, v = !1;
                        return {
                            s: function() {
                                s = s.call(r)
                            },
                            n: function() {
                                var r = s.next();
                                return p = r.done,
                                r
                            },
                            e: function(r) {
                                v = !0,
                                d = r
                            },
                            f: function() {
                                try {
                                    p || null == s.return || s.return()
                                } finally {
                                    if (v)
                                        throw d
                                }
                            }
                        }
                    }(document.cookie.split(";"));
                    try {
                        for (l.s(); !(a = l.n()).done; ) {
                            var f = a.value.replace(/^\s+/, "");
                            if (0 === f.indexOf(s)) {
                                var d = void 0;
                                try {
                                    d = decodeURIComponent(f.substring(s.length, f.length))
                                } catch (r) {
                                    d = unescape(f.substring(s.length, f.length))
                                }
                                return d
                            }
                        }
                    } catch (r) {
                        l.e(r)
                    } finally {
                        l.f()
                    }
                    return null
                },
                set: function(r, n, o, i, u, c, s) {
                    var l, f, d, p, v, h, y;
                    if ("number" == typeof o) {
                        var m = new Date;
                        m.setTime(m.getTime() + 1e3 * o),
                        y = m.toUTCString()
                    } else
                        y = "string" == typeof o && o;
                    document.cookie = a(l = a(f = a(d = a(p = a(v = a(h = "".concat(r, "=")).call(h, encodeURIComponent(n))).call(v, y ? ";expires=".concat(y) : "")).call(p, i ? ";path=".concat(i) : "")).call(d, u ? ";domain=".concat(u) : "")).call(f, c ? ";secure" : "")).call(l, s ? ";samesite=".concat(s) : "")
                }
            }
        }
    })
      , nf = u({
        "src/common/bridge.ts": function(r) {
            var n = tw()
              , o = tO()
              , i = ns()
              , u = r2()
              , a = r8()
              , c = t7()
              , s = tS();
            function l(r) {
                return (l = "function" == typeof n && "symbol" == typeof o ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof n && r.constructor === n && r !== n.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            function f(r, n) {
                (null == n || n > r.length) && (n = r.length);
                for (var o = 0, i = Array(n); o < n; o++)
                    i[o] = r[o];
                return i
            }
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.default = void 0;
            var d = !!navigator.userAgent.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/)
              , p = navigator.userAgent.indexOf("Android") > -1 || navigator.userAgent.indexOf("Adr") > -1 || navigator.userAgent.indexOf("ohos-tongdao-app") > -1;
            function v(r, n, o) {
                window.BridgeHandle[r][n] ? window.BridgeHandle[r][n].push(o) : window.BridgeHandle[r][n] = [o]
            }
            window.BridgeHandle ? (window.BridgeHandle.registerHandler || (window.BridgeHandle.registerHandler = {}),
            window.BridgeHandle.callHandler || (window.BridgeHandle.callHandler = {})) : window.BridgeHandle = {
                callHandler: {},
                registerHandler: {}
            },
            r.default = {
                callHandler: function(r, n, o) {
                    v("callHandler", r, o),
                    p ? function(r, n, o) {
                        window["".concat(r, "Callback")] = o;
                        try {
                            var i, u = c(n) || c({});
                            null !== (i = window) && void 0 !== i && null !== (i = i.StarBridge) && void 0 !== i && i[r] && window.StarBridge[r](u)
                        } catch (r) {}
                    }(r, n, o) : d && function(r) {
                        if (window.WebViewJavascriptBridge)
                            return r(window.WebViewJavascriptBridge);
                        if (document.addEventListener("WebViewJavascriptBridgeReady", function() {
                            return r(window.WebViewJavascriptBridge)
                        }, !1),
                        window.WVJBCallbacks)
                            return window.WVJBCallbacks.push(r);
                        window.WVJBCallbacks = [r];
                        var n = document.createElement("iframe");
                        n.style.display = "none",
                        n.src = "wvjbscheme://__BRIDGE_LOADED__",
                        document.documentElement.appendChild(n),
                        setTimeout(function() {
                            document.documentElement.removeChild(n)
                        }, 0)
                    }(function(i) {
                        i.callHandler(r, n, o)
                    })
                },
                registerHandler: function(r, o) {
                    v("registerHandler", r, o),
                    window[r] = function(r, o) {
                        s(window.BridgeHandle.registerHandler).forEach(function(s) {
                            var d, p = function(r, o) {
                                var c = void 0 !== n && i(r) || r["@@iterator"];
                                if (!c) {
                                    if (Array.isArray(r) || (c = function(r, n) {
                                        if (r) {
                                            if ("string" == typeof r)
                                                return f(r, void 0);
                                            var o, i = u(o = ({}).toString.call(r)).call(o, 8, -1);
                                            return "Object" === i && r.constructor && (i = r.constructor.name),
                                            "Map" === i || "Set" === i ? a(r) : "Arguments" === i || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i) ? f(r, void 0) : void 0
                                        }
                                    }(r))) {
                                        c && (r = c);
                                        var s = 0
                                          , l = function() {};
                                        return {
                                            s: l,
                                            n: function() {
                                                return s >= r.length ? {
                                                    done: !0
                                                } : {
                                                    done: !1,
                                                    value: r[s++]
                                                }
                                            },
                                            e: function(r) {
                                                throw r
                                            },
                                            f: l
                                        }
                                    }
                                    throw TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")
                                }
                                var d, p = !0, v = !1;
                                return {
                                    s: function() {
                                        c = c.call(r)
                                    },
                                    n: function() {
                                        var r = c.next();
                                        return p = r.done,
                                        r
                                    },
                                    e: function(r) {
                                        v = !0,
                                        d = r
                                    },
                                    f: function() {
                                        try {
                                            p || null == c.return || c.return()
                                        } finally {
                                            if (v)
                                                throw d
                                        }
                                    }
                                }
                            }(window.BridgeHandle.registerHandler[s]);
                            try {
                                for (p.s(); !(d = p.n()).done; ) {
                                    var v = d.value;
                                    try {
                                        var h = "object" === l(r) ? c(r) : r;
                                        null == v || v(h, o)
                                    } catch (r) {}
                                }
                            } catch (r) {
                                p.e(r)
                            } finally {
                                p.f()
                            }
                        })
                    }
                }
            }
        }
    })
      , nd = u({
        "src/common/util.ts": function(r) {
            var o = r$()
              , i = tS()
              , u = tZ()
              , a = t7()
              , c = r2()
              , s = r8()
              , l = nn()
              , f = tM();
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.addEventListener = w,
            r.asyncThrowError = m,
            r.checkLiepinApp = T,
            r.dateFormat = function(r, n) {
                var o, i = n, u = r;
                function a(r, n) {
                    i = i.replace(r, n)
                }
                "string" == typeof u && (i = u,
                u = new Date),
                i = i || "yyyy-MM-dd HH:mm:ss";
                var s = (u = u || new Date).getFullYear()
                  , l = u.getMonth() + 1
                  , f = u.getDate()
                  , d = u.getHours()
                  , p = u.getMinutes()
                  , v = u.getSeconds()
                  , h = u.getMilliseconds();
                return a(/yyyy/g, g(s, 4)),
                a(/yy/g, g(parseInt(c(o = s.toString()).call(o, 2), 10), 2)),
                a(/MM/g, g(l, 2)),
                a(/M/g, l),
                a(/dd/g, g(f, 2)),
                a(/d/g, f),
                a(/HH/g, g(d, 2)),
                a(/H/g, d),
                a(/hh/g, g(d % 12, 2)),
                a(/h/g, d % 12),
                a(/mm/g, g(p, 2)),
                a(/m/g, p),
                a(/ss/g, g(v, 2)),
                a(/s/g, v),
                a(/SSS/g, g(h, 3)),
                a(/S/g, h),
                i
            }
            ,
            r.dispatch = function(r) {
                var n, o = null === (n = window) || void 0 === n || null === (n = n.history) || void 0 === n ? void 0 : n[r];
                return function() {
                    var n = null == o ? void 0 : o.apply(this, arguments)
                      , i = null;
                    if (window.ActiveXObject || "ActiveXObject"in window) {
                        var u = document.createEvent("HTMLEvents");
                        u.initEvent(r, !1, !0),
                        i = u
                    } else
                        i = new Event(r);
                    return i.arguments = arguments,
                    window.dispatchEvent(i),
                    n
                }
            }
            ,
            r.generateSequence = function() {
                try {
                    var r, n = p.cookie.get("__session_seq") || 0;
                    return ++n ? (p.cookie.set("__session_seq", n, "", "/", b()),
                    {
                        session_seq: parseInt(n, 10)
                    }) : (r = {
                        session_seq: n
                    },
                    p.cookie.set("__session_seq", n, "", "/", b()),
                    r)
                } catch (r) {
                    return m(r),
                    {}
                }
            }
            ,
            r.generateSessionId = function() {
                try {
                    var r, n = p.cookie.get("__tlog");
                    if (n) {
                        var o = n.split("|");
                        o.length > 0 && o[0] && (r = o[0])
                    }
                    return r || (r = p.cookie.get("__sessionId")),
                    r || (r = x()),
                    p.cookie.set("__sessionId", r, "", "/", b()),
                    {
                        sessionId: r
                    }
                } catch (r) {
                    return m(r),
                    {}
                }
            }
            ,
            r.generateUuid = function() {
                var r = p.cookie.get("__uuid");
                return r || (r = x(),
                p.cookie.set("__uuid", r, 63072e4, "/", b())),
                r
            }
            ,
            r.getAppUuid = function(r) {
                T() && v.default.callHandler("getAppDataInfo", {}, function(n) {
                    try {
                        var o = JSON.parse(n).osDataInfo;
                        null != o && o.ap_uuid && (p.cookie.set("__uuid", o.ap_uuid, 63072e4, "/", b()),
                        "function" == typeof r && r(o.ap_uuid))
                    } catch (r) {
                        m(r)
                    }
                })
            }
            ,
            r.getClientSize = E,
            r.getDomain = b,
            r.getEquipment = function() {
                var r, n = !1;
                return r = navigator.userAgent || navigator.vendor || window.opera,
                (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(r) || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(r.substr(0, 4))) && (n = !0),
                n ? "h5" : "pc"
            }
            ,
            r.getMd5 = function(r) {
                return (0,
                d.default)(r)
            }
            ,
            r.getQuery = function(r, n) {
                var o = n;
                -1 !== (o = o || "".concat(window.location.href)).indexOf("#") && (o = o.substring(0, o.indexOf("#")));
                for (var i, u = [], a = RegExp("(^|\\?|&)".concat(r, "=([^&]*)(?=&|#|$)"), "g"); null !== (i = a.exec(o)); )
                    u.push(decodeURIComponent(i[2]));
                return 0 === u.length ? null : 1 === u.length ? u[0] : u
            }
            ,
            r.getScrollPosition = function() {
                var r, n, o, i, u = null === (r = document) || void 0 === r || null === (r = r.documentElement) || void 0 === r ? void 0 : r.scrollTop, a = null === (n = document) || void 0 === n || null === (n = n.body) || void 0 === n ? void 0 : n.scrollTop, c = null === (o = document) || void 0 === o || null === (o = o.documentElement) || void 0 === o ? void 0 : o.scrollLeft, s = null === (i = document) || void 0 === i || null === (i = i.body) || void 0 === i ? void 0 : i.scrollLeft;
                return {
                    y: window.pageYOffset || u || a,
                    x: window.pageXOffset || c || s
                }
            }
            ,
            r.getUuid = x,
            r.hasHashNode = function() {
                var r = window.location.hash
                  , n = document.getElementById(null == r ? void 0 : r.replace("#", ""))
                  , o = !1;
                return n && (o = !0),
                o
            }
            ,
            r.isArray = function(r) {
                return Array.isArray(r)
            }
            ,
            r.isElementInViewport = function(r, n) {
                if (!O(r))
                    return !1;
                var o = r.getBoundingClientRect()
                  , i = E()
                  , u = i.x
                  , a = i.y;
                if (n) {
                    var c = n.getBoundingClientRect();
                    return Math.floor(o.top) >= Math.max(0, Math.floor(c.top)) && Math.floor(o.left) >= Math.max(0, Math.floor(c.left)) && Math.floor(o.right) <= Math.min(u, Math.floor(c.right)) && Math.floor(o.bottom) <= Math.min(a, Math.floor(c.bottom))
                }
                return o.top >= 0 && o.left >= 0 && Math.floor(o.bottom) <= Math.floor(a) && Math.floor(o.right) <= Math.floor(u)
            }
            ,
            r.isInvalidPgRef = function(r) {
                var n, o, i = null === (n = decodeURIComponent(r).split("@")) || void 0 === n || null === (n = n[0]) || void 0 === n ? void 0 : n.split(":");
                return !(null == i || null === (o = f(i).call(i, function(r) {
                    return !r
                })) || void 0 === o || !o.length)
            }
            ,
            r.isObject = y,
            r.isString = function(r) {
                return "[object String]" === Object.prototype.toString.call(r)
            }
            ,
            r.isVisible = O,
            r.lastTime = function() {
                var r = new Date;
                return r.setHours(0, 0, 0, 0),
                864e5 - (_() - r.getTime())
            }
            ,
            r.mutationCallBack = function(r, n, o, i, u, a) {
                try {
                    return function(c) {
                        a && clearTimeout(a),
                        a = setTimeout(function() {
                            c.forEach(function(a) {
                                var c = o.dynamic[r];
                                if ("childList" === a.type) {
                                    if (a.addedNodes) {
                                        var f = a.addedNodes;
                                        s(f).forEach(function(r) {
                                            r.nodeType && 1 === r.nodeType && r.matches(n) && c.listening.push(r)
                                        })
                                    }
                                    if (a.removedNodes) {
                                        var d = a.removedNodes;
                                        s(d).forEach(function(r) {
                                            var n, o = i(c.listening, r);
                                            o > -1 && l(n = c.listening).call(n, o, 1)
                                        })
                                    }
                                    u(r)
                                } else
                                    "attributes" === a.type && "style" === a.attributeName && u(r)
                            })
                        }, 100)
                    }
                } catch (r) {
                    return m(r),
                    function() {}
                }
            }
            ,
            r.now = _,
            r.param = function(r) {
                var n;
                return y(r) ? o(n = i(r)).call(n, function(n) {
                    var o;
                    return u(o = "".concat(encodeURIComponent(n), "=")).call(o, encodeURIComponent(a(r[n])))
                }).join("&") : ""
            }
            ,
            r.removeEventListener = j,
            r.setEventSeq = function() {
                var r = p.cookie.get("__tlg_event_seq") || 0;
                return r -= 0,
                r++,
                p.cookie.set("__tlg_event_seq", r, "", "/", b()),
                r
            }
            ,
            r.spliceDate = g,
            r.tlogReady = P,
            r.uuidV4 = function() {
                var r = (new Date).getTime()
                  , n = "undefined" != typeof performance && performance.now && 1e3 * performance.now() || 0;
                return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function(o) {
                    var i = 16 * Math.random();
                    return r > 0 ? (i = Math.floor((r + i) % 16),
                    r = Math.floor(r / 16)) : (i = Math.floor((n + i) % 16),
                    n = Math.floor(n / 16)),
                    ("x" === o ? i : i / 4 + 8).toString(16)
                })
            }
            ;
            var d = h(no())
              , p = nl()
              , v = h(nf());
            function h(r) {
                return r && r.__esModule ? r : {
                    default: r
                }
            }
            function y(r) {
                return "[object Object]" === Object.prototype.toString.call(r)
            }
            function m(r) {
                var o = r;
                n(o, Error) || (o = Error(o)),
                setTimeout(function() {
                    throw o
                }, 0)
            }
            function g(r, n) {
                var o = ""
                  , i = String(Math.abs(r));
                return i.length < n && (o = Array(n - i.length + 1).join("0")),
                (r < 0 ? "-" : "") + o + i
            }
            function b() {
                var r, n;
                return ".".concat(null === (n = document.domain) || void 0 === n ? void 0 : c(r = n.split(".")).call(r, -2).join("."))
            }
            function j(r, n, o, i) {
                return r.removeEventListener ? (r.removeEventListener(n, o, i || !0),
                !0) : r.detachEvent ? r.detachEvent("on".concat(n), o) : (r["on".concat(n)] = "",
                null)
            }
            function w(r, n, o, i) {
                return r.addEventListener ? (r.addEventListener(n, o, i || !0),
                !0) : r.attachEvent ? r.attachEvent("on".concat(n), o) : (r["on".concat(n)] = o,
                null)
            }
            function x() {
                return (Number(new Date) + Math.random()).toFixed(2)
            }
            function _() {
                return Date.now()
            }
            function E() {
                var r, n, o = null === (r = document) || void 0 === r || null === (r = r.documentElement) || void 0 === r ? void 0 : r.clientWidth, i = null === (n = document) || void 0 === n || null === (n = n.documentElement) || void 0 === n ? void 0 : n.clientHeight;
                return {
                    x: window.innerWidth || o,
                    y: window.innerHeight || i
                }
            }
            function O(r) {
                var n;
                return !!((null == r ? void 0 : r.offsetWidth) || (null == r ? void 0 : r.offsetHeight) || (null == r || null === (n = r.getClientRects) || void 0 === n || null === (n = n.call(r)) || void 0 === n ? void 0 : n.length))
            }
            function T() {
                var r, n, o = !1, i = null === (r = window) || void 0 === r || null === (r = r.navigator) || void 0 === r || null === (r = r.userAgent) || void 0 === r || null === (n = r.toLocaleLowerCase) || void 0 === n ? void 0 : n.call(r);
                return ((null == i ? void 0 : i.indexOf("ios-tongdao-app")) > -1 || (null == i ? void 0 : i.indexOf("android-tongdao-app")) > -1 || (null == i ? void 0 : i.indexOf("ohos-tongdao-app")) > -1) && (o = !0),
                o
            }
            var k = !1
              , S = [];
            function P(r) {
                k ? (S.length && (S.forEach(function(r) {
                    r()
                }),
                S = []),
                "function" == typeof r && r()) : "function" == typeof r && S.push(r)
            }
            function C() {
                k = !0,
                P()
            }
            "complete" === document.readyState || "interactive" === document.readyState ? window.setTimeout(C) : w(document, "DOMContentLoaded", function r() {
                null == C || C(),
                j(document, "DOMContentLoaded", r)
            })
        }
    })
      , np = u({
        "src/configManager/defaultConfig.ts": function(r) {
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.default = void 0;
            var n = nd();
            r.default = {
                config: {
                    reportUrl: "//statistic".concat((0,
                    n.getDomain)(), "/statisticPlatform/standardTLog.json"),
                    reportCustomUrl: "//statistic".concat((0,
                    n.getDomain)(), "/statisticPlatform/customEventTLog.json")
                },
                preStartQueueMaxCount: 100,
                accountId: "",
                collect: {
                    click: {
                        enable: !0
                    },
                    exposure: {
                        enable: !0,
                        exposureInterval: 1e3,
                        maxSendCount: 100,
                        config: []
                    },
                    alive: {
                        enable: !0
                    },
                    pageView: {
                        enable: !0
                    },
                    showDialog: {
                        enable: !0,
                        dialogAlias: ["vdialog", "educate-shade-content", "bubble-tips-box", "tlg-dialog", "dialog"]
                    }
                },
                dialogAlias: ["vdialog", "educate-shade-content", "bubble-tips-box", "tlg-dialog", "dialog"],
                exposure: [],
                ignoreAction: [],
                pageId: "",
                scm: {},
                ext: {},
                allowHash: !1,
                spa: !0
            }
        }
    })
      , nv = u({
        "node_modules/core-js-pure/internals/freezing.js": function(r, n) {
            n.exports = !c()(function() {
                return Object.isExtensible(Object.preventExtensions({}))
            })
        }
    })
      , nh = u({
        "node_modules/core-js-pure/internals/define-built-ins.js": function(r, n) {
            var o = eR();
            n.exports = function(r, n, i) {
                for (var u in n)
                    i && i.unsafe && r[u] ? r[u] = n[u] : o(r, u, n[u], i);
                return r
            }
        }
    })
      , ny = u({
        "node_modules/core-js-pure/internals/array-buffer-non-extensible.js": function(r, n) {
            n.exports = c()(function() {
                if ("function" == typeof ArrayBuffer) {
                    var r = new ArrayBuffer(8);
                    Object.isExtensible(r) && Object.defineProperty(r, "a", {
                        value: 8
                    })
                }
            })
        }
    })
      , nm = u({
        "node_modules/core-js-pure/internals/object-is-extensible.js": function(r, n) {
            var o = c()
              , i = _()
              , u = d()
              , a = ny()
              , s = Object.isExtensible;
            n.exports = o(function() {
                s(1)
            }) || a ? function(r) {
                return !!i(r) && (!a || "ArrayBuffer" !== u(r)) && (!s || s(r))
            }
            : s
        }
    })
      , ng = u({
        "node_modules/core-js-pure/internals/internal-metadata.js": function(r, n) {
            var i = et()
              , u = f()
              , a = ew()
              , c = _()
              , s = q()
              , l = Z().f
              , d = eP()
              , p = eA()
              , v = nm()
              , h = H()
              , y = nv()
              , m = !1
              , g = h("meta")
              , b = 0
              , j = function(r) {
                l(r, g, {
                    value: {
                        objectID: "O" + b++,
                        weakData: {}
                    }
                })
            }
              , w = n.exports = {
                enable: function() {
                    w.enable = function() {}
                    ,
                    m = !0;
                    var r = d.f
                      , n = u([].splice)
                      , o = {};
                    o[g] = 1,
                    r(o).length && (d.f = function(o) {
                        for (var i = r(o), u = 0, a = i.length; u < a; u++)
                            if (i[u] === g) {
                                n(i, u, 1);
                                break
                            }
                        return i
                    }
                    ,
                    i({
                        target: "Object",
                        stat: !0,
                        forced: !0
                    }, {
                        getOwnPropertyNames: p.f
                    }))
                },
                fastKey: function(r, n) {
                    if (!c(r))
                        return "symbol" == (void 0 === r ? "undefined" : o(r)) ? r : ("string" == typeof r ? "S" : "P") + r;
                    if (!s(r, g)) {
                        if (!v(r))
                            return "F";
                        if (!n)
                            return "E";
                        j(r)
                    }
                    return r[g].objectID
                },
                getWeakData: function(r, n) {
                    if (!s(r, g)) {
                        if (!v(r))
                            return !0;
                        if (!n)
                            return !1;
                        j(r)
                    }
                    return r[g].weakData
                },
                onFreeze: function(r) {
                    return y && m && v(r) && !s(r, g) && j(r),
                    r
                }
            };
            a[g] = !0
        }
    })
      , nb = u({
        "node_modules/core-js-pure/internals/collection.js": function(r, n) {
            var o = et()
              , i = a()
              , u = ng()
              , s = c()
              , l = ee()
              , f = rc()
              , d = rh()
              , p = v()
              , y = _()
              , m = j()
              , g = eU()
              , b = Z().f
              , w = eH().forEach
              , x = h()
              , E = eq()
              , O = E.set
              , T = E.getterFor;
            n.exports = function(r, n, a) {
                var c, v = -1 !== r.indexOf("Map"), h = -1 !== r.indexOf("Weak"), j = v ? "set" : "add", _ = i[r], E = _ && _.prototype, k = {};
                if (x && p(_) && (h || E.forEach && !s(function() {
                    (new _).entries().next()
                }))) {
                    var S = (c = n(function(n, o) {
                        O(d(n, S), {
                            type: r,
                            collection: new _
                        }),
                        m(o) || f(o, n[j], {
                            that: n,
                            AS_ENTRIES: v
                        })
                    })).prototype
                      , P = T(r);
                    w(["add", "clear", "delete", "forEach", "get", "has", "set", "keys", "values", "entries"], function(r) {
                        var n = "add" === r || "set" === r;
                        r in E && (!h || "clear" !== r) && l(S, r, function(o, i) {
                            var u = P(this).collection;
                            if (!n && h && !y(o))
                                return "get" === r && void 0;
                            var a = u[r](0 === o ? 0 : o, i);
                            return n ? this : a
                        })
                    }),
                    h || b(S, "size", {
                        configurable: !0,
                        get: function() {
                            return P(this).collection.size
                        }
                    })
                } else
                    c = a.getConstructor(n, r, v, j),
                    u.enable();
                return g(c, r, !1, !0),
                k[r] = c,
                o({
                    global: !0,
                    forced: !0
                }, k),
                h || a.setStrong(c, r, v),
                c
            }
        }
    })
      , nj = u({
        "node_modules/core-js-pure/internals/collection-weak.js": function(r, n) {
            var o = f()
              , i = nh()
              , u = ng().getWeakData
              , a = rh()
              , c = $()
              , s = j()
              , l = _()
              , d = rc()
              , p = eH()
              , v = q()
              , h = eq()
              , y = h.set
              , m = h.getterFor
              , g = p.find
              , b = p.findIndex
              , w = o([].splice)
              , x = 0
              , E = function(r) {
                return r.frozen || (r.frozen = new O)
            }
              , O = function() {
                this.entries = []
            }
              , T = function(r, n) {
                return g(r.entries, function(r) {
                    return r[0] === n
                })
            };
            O.prototype = {
                get: function(r) {
                    var n = T(this, r);
                    if (n)
                        return n[1]
                },
                has: function(r) {
                    return !!T(this, r)
                },
                set: function(r, n) {
                    var o = T(this, r);
                    o ? o[1] = n : this.entries.push([r, n])
                },
                delete: function(r) {
                    var n = b(this.entries, function(n) {
                        return n[0] === r
                    });
                    return ~n && w(this.entries, n, 1),
                    !!~n
                }
            },
            n.exports = {
                getConstructor: function(r, n, o, f) {
                    var p = r(function(r, i) {
                        a(r, h),
                        y(r, {
                            type: n,
                            id: x++,
                            frozen: null
                        }),
                        s(i) || d(i, r[f], {
                            that: r,
                            AS_ENTRIES: o
                        })
                    })
                      , h = p.prototype
                      , g = m(n)
                      , b = function(r, n, o) {
                        var i = g(r)
                          , a = u(c(n), !0);
                        return !0 === a ? E(i).set(n, o) : a[i.id] = o,
                        r
                    };
                    return i(h, {
                        delete: function(r) {
                            var n = g(this);
                            if (!l(r))
                                return !1;
                            var o = u(r);
                            return !0 === o ? E(n).delete(r) : o && v(o, n.id) && delete o[n.id]
                        },
                        has: function(r) {
                            var n = g(this);
                            if (!l(r))
                                return !1;
                            var o = u(r);
                            return !0 === o ? E(n).has(r) : o && v(o, n.id)
                        }
                    }),
                    i(h, o ? {
                        get: function(r) {
                            var n = g(this);
                            if (l(r)) {
                                var o = u(r);
                                if (!0 === o)
                                    return E(n).get(r);
                                if (o)
                                    return o[n.id]
                            }
                        },
                        set: function(r, n) {
                            return b(this, r, n)
                        }
                    } : {
                        add: function(r) {
                            return b(this, r, !0)
                        }
                    }),
                    p
                }
            }
        }
    })
      , nw = u({
        "node_modules/core-js-pure/modules/es.weak-map.constructor.js": function() {
            var r, n, o, i, u = nv(), s = a(), l = f(), d = nh(), p = ng(), v = nb(), h = nj(), y = _(), m = eq().enforce, g = c(), b = eF(), j = Object, w = Array.isArray, x = j.isExtensible, E = j.isFrozen, O = j.isSealed, T = j.freeze, k = j.seal, S = !s.ActiveXObject && "ActiveXObject"in s, P = function(r) {
                return function() {
                    return r(this, arguments.length ? arguments[0] : void 0)
                }
            }, C = v("WeakMap", P, h), A = C.prototype, I = l(A.set);
            b && (S ? (r = h.getConstructor(P, "WeakMap", !0),
            p.enable(),
            n = l(A.delete),
            o = l(A.has),
            i = l(A.get),
            d(A, {
                delete: function(o) {
                    if (y(o) && !x(o)) {
                        var i = m(this);
                        return i.frozen || (i.frozen = new r),
                        n(this, o) || i.frozen.delete(o)
                    }
                    return n(this, o)
                },
                has: function(n) {
                    if (y(n) && !x(n)) {
                        var i = m(this);
                        return i.frozen || (i.frozen = new r),
                        o(this, n) || i.frozen.has(n)
                    }
                    return o(this, n)
                },
                get: function(n) {
                    if (y(n) && !x(n)) {
                        var u = m(this);
                        return u.frozen || (u.frozen = new r),
                        o(this, n) ? i(this, n) : u.frozen.get(n)
                    }
                    return i(this, n)
                },
                set: function(n, i) {
                    if (y(n) && !x(n)) {
                        var u = m(this);
                        u.frozen || (u.frozen = new r),
                        o(this, n) ? I(this, n, i) : u.frozen.set(n, i)
                    } else
                        I(this, n, i);
                    return this
                }
            })) : u && g(function() {
                var r = T([]);
                return I(new C, r, 1),
                !E(r)
            }) && d(A, {
                set: function(r, n) {
                    var o;
                    return w(r) && (E(r) ? o = T : O(r) && (o = k)),
                    I(this, r, n),
                    o && o(r),
                    this
                }
            }))
        }
    })
      , nx = u({
        "node_modules/core-js-pure/modules/es.weak-map.js": function() {
            nw()
        }
    })
      , n_ = u({
        "node_modules/core-js-pure/es/weak-map/index.js": function(r, n) {
            tg(),
            em(),
            nx(),
            n.exports = E().WeakMap
        }
    })
      , nE = u({
        "node_modules/core-js-pure/stable/weak-map/index.js": function(r, n) {
            var o = n_();
            tj(),
            n.exports = o
        }
    })
      , nO = u({
        "node_modules/core-js-pure/internals/whitespaces.js": function(r, n) {
            n.exports = "	\n\v\f\r                　\u2028\u2029\uFEFF"
        }
    })
      , nT = u({
        "node_modules/core-js-pure/internals/string-trim.js": function(r, n) {
            var o = f()
              , i = w()
              , u = eg()
              , a = nO()
              , c = o("".replace)
              , s = RegExp("^[" + a + "]+")
              , l = RegExp("(^|[^" + a + "])[" + a + "]+$")
              , d = function(r) {
                return function(n) {
                    var o = u(i(n));
                    return 1 & r && (o = c(o, s, "")),
                    2 & r && (o = c(o, l, "$1")),
                    o
                }
            };
            n.exports = {
                start: d(1),
                end: d(2),
                trim: d(3)
            }
        }
    })
      , nk = u({
        "node_modules/core-js-pure/internals/string-trim-forced.js": function(r, n) {
            var o = ta().PROPER
              , i = c()
              , u = nO();
            n.exports = function(r) {
                return i(function() {
                    return !!u[r]() || "​᠎" !== "​᠎"[r]() || o && u[r].name !== r
                })
            }
        }
    })
      , nS = u({
        "node_modules/core-js-pure/modules/es.string.trim.js": function() {
            var r = et()
              , n = nT().trim;
            r({
                target: "String",
                proto: !0,
                forced: nk()("trim")
            }, {
                trim: function() {
                    return n(this)
                }
            })
        }
    })
      , nP = u({
        "node_modules/core-js-pure/es/string/virtual/trim.js": function(r, n) {
            nS(),
            n.exports = tI()("String", "trim")
        }
    })
      , nC = u({
        "node_modules/core-js-pure/es/instance/trim.js": function(r, n) {
            var o = T()
              , i = nP()
              , u = String.prototype;
            n.exports = function(r) {
                var n = r.trim;
                return "string" == typeof r || r === u || o(u, r) && n === u.trim ? i : n
            }
        }
    })
      , nA = u({
        "node_modules/core-js-pure/stable/instance/trim.js": function(r, n) {
            n.exports = nC()
        }
    })
      , nI = u({
        "src/common/constant.ts": function(r) {
            var n, o;
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.UrlRegexp = r.TLOG_VERSION_KEY = r.TLOG_TEST_KEY = r.STORAGE_KEY = r.ReportEventType = r.PGREF_DEFAULT_APPCODE = r.LifecycleEvent = r.InlineTag = r.IndexTag = r.IgnoreClass = r.EventTypes = r.DialogClass = r.AUTOTRACK_KEY = void 0,
            r.STORAGE_KEY = "lp_tlog_storage",
            r.TLOG_TEST_KEY = "_tlog-test-key",
            r.AUTOTRACK_KEY = "$auto_",
            r.TLOG_VERSION_KEY = "3.0",
            r.PGREF_DEFAULT_APPCODE = "-1:-1@-1:-1:-1",
            r.EventTypes = {
                p: "pageView",
                c: "click",
                e: "exposure",
                s: "showDialog",
                a: "alive"
            },
            (n = {}).pageView = "p",
            n.click = "c",
            n.exposure = "e",
            n.showDialog = "s",
            n.alive = "a",
            n.customEvent = "CE",
            r.ReportEventType = n,
            r.DialogClass = ["vdialog", "educate-shade-content", "bubble-tips-box", "tlg-dialog", "dialog"],
            r.IgnoreClass = /^(clear|clearfix|active|hover|enabled|hidden|display|focus|disable|disabled|show|hide|wrap|tlg-ext-hover|tlg-ext-selected|selected)/,
            r.InlineTag = ["i", "a", "b", "u", "em", "abbr", "big", "cite", "code", "dfn", "span", "sup", "sub", "label", "button"],
            r.IndexTag = ["tr", "li", "dl"],
            (o = {}).init = "init",
            o.start = "start",
            o.beforeConfig = "beforeConfig",
            o.config = "config",
            o.report = "report",
            o.beforeBuild = "beforeBuild",
            o.build = "build",
            o.onReady = "onReady",
            o.beforeSend = "beforeSend",
            o.send = "send",
            o.beforeDestroy = "beforeDestroy",
            o.destroy = "destroy",
            r.LifecycleEvent = o,
            r.UrlRegexp = /^(?:https?:\/\/)?([^/]+)/i
        }
    })
      , nR = u({
        "src/collect/base.ts": function(r) {
            var o, i, u = tw(), a = tO(), c = tS(), s = tC(), l = tM(), f = tB(), d = tH(), p = tG(), v = tZ(), h = r$(), y = nA(), m = r8(), g = t7();
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.default = void 0;
            var b, j = (b = no()) && b.__esModule ? b : {
                default: b
            }, w = nI(), x = nd();
            function _(r) {
                return (_ = "function" == typeof u && "symbol" == typeof a ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof u && r.constructor === u && r !== u.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            function E(r, n) {
                var o = c(r);
                if (s) {
                    var i = s(r);
                    n && (i = l(i).call(i, function(n) {
                        return f(r, n).enumerable
                    })),
                    o.push.apply(o, i)
                }
                return o
            }
            function O(r) {
                for (var n = 1; n < arguments.length; n++) {
                    var o = null != arguments[n] ? arguments[n] : {};
                    n % 2 ? E(Object(o), !0).forEach(function(n) {
                        var i, u, a;
                        i = r,
                        u = n,
                        a = o[n],
                        (u = T(u))in i ? Object.defineProperty(i, u, {
                            value: a,
                            enumerable: !0,
                            configurable: !0,
                            writable: !0
                        }) : i[u] = a
                    }) : d ? Object.defineProperties(r, d(o)) : E(Object(o)).forEach(function(n) {
                        Object.defineProperty(r, n, f(o, n))
                    })
                }
                return r
            }
            function T(r) {
                var n = function(r, n) {
                    if ("object" != _(r) || !r)
                        return r;
                    var o = r[p];
                    if (void 0 !== o) {
                        var i = o.call(r, n || "default");
                        if ("object" != _(i))
                            return i;
                        throw TypeError("@@toPrimitive must return a primitive value.")
                    }
                    return ("string" === n ? String : Number)(r)
                }(r, "string");
                return "symbol" == _(n) ? n : n + ""
            }
            o = function r() {
                var o, i = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : {};
                (function(r, o) {
                    if (!n(r, o))
                        throw TypeError("Cannot call a class as a function")
                }
                )(this, r),
                this.polyfillElementMatches(),
                this.opts = i;
                var u = w.DialogClass
                  , a = null == i ? void 0 : i.dialogAlias;
                a && ("string" == typeof a ? u.push(a) : Array.isArray(a) && (u = v(u).call(u, a))),
                this.dialogReg = new RegExp("(^|\\s+)(".concat(null === (o = u) || void 0 === o || null === (o = h(o).call(o, function(r) {
                    return r.replace(/^\./, "")
                })) || void 0 === o ? void 0 : o.join("|"), ")(\\s+|$)"))
            }
            ,
            i = [{
                key: "attr",
                value: function(r, n, o) {
                    return o ? (r.setAttribute(n, o),
                    null) : r.getAttribute(n)
                }
            }, {
                key: "isDialog",
                value: function(r) {
                    var n, o, i, u, a = null == r ? void 0 : r.children;
                    return !(null == a || !a.length || "div" !== (null === (n = a[0]) || void 0 === n || null === (n = n.tagName) || void 0 === n || null === (o = n.toLowerCase) || void 0 === o ? void 0 : o.call(n)) || "ant-modal-root" !== (null === (i = a[0]) || void 0 === i ? void 0 : i.className)) || !(null == r || null === (u = r.querySelector) || void 0 === u || !u.call(r, ".tlg-dialog")) || this.dialogReg.test(this.attr(r, "class"))
                }
            }, {
                key: "getDialogScmAndElemId",
                value: function(r) {
                    try {
                        var n, o, i = r.children;
                        return i.length && "div" === i[0].tagName.toLowerCase() && "ant-modal-root" === i[0].className || r.querySelector(".tlg-aba-data-node") ? null != r && null !== (o = r.querySelector) && void 0 !== o && o.call(r, ".tlg-aba-data-node") ? this.xpath(r.querySelector(".tlg-aba-data-node")) : this.xpath(i[0]) : null != r && null !== (n = r.querySelector) && void 0 !== n && n.call(r, ".tlg-dialog") ? this.xpath(r.querySelector(".tlg-dialog")) : {}
                    } catch (r) {
                        return {}
                    }
                }
            }, {
                key: "notations",
                value: function(r) {
                    var n = w.IgnoreClass
                      , o = this.attr(r, "class")
                      , i = this.attr(r, "id") || "";
                    return /nodetpl_/.test(i) && (i = ""),
                    o && (o = l(o = y(o).call(o).replace(/\s{2,}/g, " ").split(" ")).call(o, function(r) {
                        return !n.test(r)
                    }).join(".")),
                    (i ? "#".concat(y(i).call(i)) : "") + (o ? ".".concat(o) : "")
                }
            }, {
                key: "indexOf",
                value: function(r, n) {
                    var o;
                    return null === (o = m(r)) || void 0 === o || null === (o = l(o).call(o, function(r) {
                        return 1 === r.nodeType && r.tagName === n.tagName
                    })) || void 0 === o ? void 0 : o.indexOf(n)
                }
            }, {
                key: "xpath",
                value: function(r) {
                    for (var n, o = [], i = w.IndexTag, u = w.InlineTag, a = -1, c = {}, s = r, l = r, f = 0, d = "", p = {}, v = {}; n = null === (h = r) || void 0 === h || null === (h = h.tagName) || void 0 === h || null === (y = h.toLowerCase) || void 0 === y ? void 0 : y.call(h),
                    u.indexOf(n) > -1 && "body" !== n && "html" !== n; ) {
                        if ("a" === n || "button" === n) {
                            c.text = this.getTextByInLineTagTextNode(r);
                            break
                        }
                        if (!r.parentNode)
                            break;
                        var h, y, m, b, j, _ = r.parentNode, E = null == _ || null === (m = _.tagName) || void 0 === m || null === (b = (j = m).toLowerCase) || void 0 === b ? void 0 : b.call(j);
                        if (0 > u.indexOf(E)) {
                            c.text = this.getTextByInLineTagTextNode(r);
                            break
                        }
                        if (s = r,
                        r = _,
                        ++f > 10) {
                            s = l,
                            r = l;
                            break
                        }
                    }
                    for (; "body" !== (n = null === (T = r) || void 0 === T || null === (T = T.tagName) || void 0 === T || null === (k = T.toLowerCase) || void 0 === k ? void 0 : k.call(T)) && "html" !== n && r.parentNode; ) {
                        var T, k, S = r.parentNode, P = this.attr(r, "data-tlg-index");
                        -1 === a && (P ? a = P : i.indexOf(n) > -1 && (a = this.indexOf(S.childNodes, r)));
                        var C = this.attr(r, "data-info");
                        if (C)
                            c = O(O({}, this.query2JSON(C)), c);
                        else if (C = this.attr(r, "data_info"))
                            try {
                                c = O(O({}, C = JSON.parse(decodeURIComponent(C))), c)
                            } catch (r) {
                                (0,
                                x.asyncThrowError)(r)
                            }
                        try {
                            if (!d) {
                                var A = this.attr(r, "data-tlg-elem-id");
                                A && (d = A)
                            }
                            if ("{}" === g(p)) {
                                var I = this.attr(r, "data-tlg-scm");
                                I && (p = this.query2JSON(I))
                            }
                            if ("{}" === g(v)) {
                                var R = this.attr(r, "data-tlg-ext");
                                R && (v = this.query2JSON(R))
                            }
                        } catch (r) {
                            (0,
                            x.asyncThrowError)(r)
                        }
                        o.unshift(n + this.notations(r)),
                        s = r,
                        r = S
                    }
                    if (o = o.join("/"),
                    this.isDialog(s)) {
                        var L = this.attr(s, "data-tlg-md5");
                        L || (L = this.elmMd5(s),
                        this.attr(s, "data-tlg-md5", L));
                        var M, N = "", D = s.querySelector(".vd-title") || s.querySelector(".tlg-title") || s.querySelector(".title") || s.querySelector(".ant-modal-title");
                        D && ((N = this.attr(D, "data-tlg-title")) || (N = null == D || null === (M = D.innerHTML) || void 0 === M ? void 0 : M.replace(/<\/?[^>]+>/g, ""),
                        this.attr(s, "data-tlg-md5", L))),
                        c.layer_md5 = L,
                        c.layer_title = N
                    }
                    return {
                        index: a,
                        xpath: o,
                        dataInfo: c,
                        scm: p,
                        ext: v,
                        elemId: d
                    }
                }
            }, {
                key: "isInLineTag",
                value: function(r) {
                    var n, o, i = w.InlineTag, u = null === (n = r.tagName) || void 0 === n || null === (o = n.toLowerCase) || void 0 === o ? void 0 : o.call(n);
                    return i.indexOf(u) > -1
                }
            }, {
                key: "getTextByInLineTagTextNode",
                value: function(r) {
                    var n, o, i = this, u = r.childNodes, a = "";
                    return null === (n = m(u)) || void 0 === n || n.forEach(function(r) {
                        3 === r.nodeType ? a += r.textContent || r.innerText || "" : 1 === r.nodeType && i.isInLineTag(r) && (a += i.getTextByInLineTagTextNode(r))
                    }),
                    a.length && (a = null === (o = a.replace(/[\r\t\n]+/g, "")) || void 0 === o ? void 0 : y(o).call(o)),
                    a
                }
            }, {
                key: "getTextByTextNode",
                value: function(r) {
                    var n, o = r.childNodes, i = "";
                    return m(o).forEach(function(r) {
                        3 === r.nodeType && (i += r.textContent || r.innerText || "")
                    }),
                    i.length && (i = null === (n = i.replace(/[\r\t\n]+/g, "")) || void 0 === n ? void 0 : y(n).call(n)),
                    i
                }
            }, {
                key: "query2JSON",
                value: function(r) {
                    var n = {}
                      , o = null;
                    if ("string" == typeof r) {
                        o = decodeURIComponent(r);
                        try {
                            n = JSON.parse(o)
                        } catch (r) {
                            var i = o.split("&");
                            null == i || i.forEach(function(r) {
                                var o = r.split("=");
                                n[o[0]] = o[1]
                            })
                        }
                    }
                    return n
                }
            }, {
                key: "elmMd5",
                value: function(r) {
                    try {
                        var n = /(\s+(?!data-tlg-)(?!src)[\w-]+(\s*=\s*['"].*?['"])?)+?/g
                          , o = this.outerHTML(r).toLowerCase().replace(n, "").replace(n, "").replace(/\d+/g, "").replace(/(<textarea[^>]*>).*?(<\/textarea>)/g, "$1$2").replace(/[\s\r\n\t]+/g, "");
                        return (0,
                        j.default)(o)
                    } catch (r) {
                        return ""
                    }
                }
            }, {
                key: "outerHTML",
                value: function(r) {
                    if ("outerHTML"in r)
                        return r.outerHTML;
                    var n = document.createElement("div");
                    return n.appendChild(r),
                    n.innerHTML
                }
            }, {
                key: "xpath2selector",
                value: function(r) {
                    return y(r).call(r).replace(/\//g, " ")
                }
            }, {
                key: "polyfillElementMatches",
                value: function() {
                    var r, n, o, i, u;
                    Element.prototype.matches || (Element.prototype.matches = (null === (r = Element.prototype) || void 0 === r ? void 0 : r.matchesSelector) || (null === (n = Element.prototype) || void 0 === n ? void 0 : n.mozMatchesSelector) || (null === (o = Element.prototype) || void 0 === o ? void 0 : o.msMatchesSelector) || (null === (i = Element.prototype) || void 0 === i ? void 0 : i.oMatchesSelector) || (null === (u = Element.prototype) || void 0 === u ? void 0 : u.webkitMatchesSelector) || function(r) {
                        for (var n, o = null === (n = this.document || this.ownerDocument) || void 0 === n ? void 0 : n.querySelectorAll(r), i = o.length; --i >= 0 && o.item(i) !== this; )
                            ;
                        return i > -1
                    }
                    )
                }
            }],
            function(r, n) {
                for (var o = 0; o < n.length; o++) {
                    var i = n[o];
                    i.enumerable = i.enumerable || !1,
                    i.configurable = !0,
                    "value"in i && (i.writable = !0),
                    Object.defineProperty(r, T(i.key), i)
                }
            }(o.prototype, i),
            Object.defineProperty(o, "prototype", {
                writable: !1
            }),
            r.default = o
        }
    })
      , nL = u({
        "src/common/log.ts": function(r) {
            var o, i, u, a = tw(), c = tO(), s = tG();
            tZ(),
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.default = void 0;
            var l = nd();
            function f(r) {
                return (f = "function" == typeof a && "symbol" == typeof c ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof a && r.constructor === a && r !== a.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            function d(r, n) {
                for (var o = 0; o < n.length; o++) {
                    var i = n[o];
                    i.enumerable = i.enumerable || !1,
                    i.configurable = !0,
                    "value"in i && (i.writable = !0),
                    Object.defineProperty(r, v(i.key), i)
                }
            }
            function p(r, n, o) {
                return (n = v(n))in r ? Object.defineProperty(r, n, {
                    value: o,
                    enumerable: !0,
                    configurable: !0,
                    writable: !0
                }) : r[n] = o,
                r
            }
            function v(r) {
                var n = function(r, n) {
                    if ("object" != f(r) || !r)
                        return r;
                    var o = r[s];
                    if (void 0 !== o) {
                        var i = o.call(r, n || "default");
                        if ("object" != f(i))
                            return i;
                        throw TypeError("@@toPrimitive must return a primitive value.")
                    }
                    return ("string" === n ? String : Number)(r)
                }(r, "string");
                return "symbol" == f(n) ? n : n + ""
            }
            o = function r() {
                var o, i, u = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : {};
                (function(r, o) {
                    if (!n(r, o))
                        throw TypeError("Cannot call a class as a function")
                }
                )(this, r),
                p(this, "options", {}),
                p(this, "debugger", !1),
                p(this, "libName", "Tlog"),
                this.options = u,
                this.libName = null !== (o = null === (i = this.options) || void 0 === i ? void 0 : i.libName) && void 0 !== o ? o : "Tlog",
                this.debugger = this.options.log || !!(0,
                l.getQuery)("debug", "")
            }
            ,
            i = [{
                key: "error",
                value: function(r, n) {
                    this.debugger && (0,
                    l.dateFormat)(new Date, "yyyy-MM-dd HH:mm:ss.SSS")
                }
            }, {
                key: "info",
                value: function(r, n) {
                    this.debugger && (0,
                    l.dateFormat)(new Date, "yyyy-MM-dd HH:mm:ss.SSS")
                }
            }],
            d(o.prototype, i),
            u && d(o, u),
            Object.defineProperty(o, "prototype", {
                writable: !1
            }),
            r.default = o
        }
    })
      , nM = u({
        "src/common/EventEmitter.ts": function(r) {
            var o, i, u, a = tw(), c = tO(), s = r2(), l = r8(), f = ns(), d = tG(), p = nn(), v = tS();
            function h(r) {
                return (h = "function" == typeof a && "symbol" == typeof c ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof a && r.constructor === a && r !== a.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            function y(r, n) {
                (null == n || n > r.length) && (n = r.length);
                for (var o = 0, i = Array(n); o < n; o++)
                    i[o] = r[o];
                return i
            }
            function m(r, n) {
                for (var o = 0; o < n.length; o++) {
                    var i = n[o];
                    i.enumerable = i.enumerable || !1,
                    i.configurable = !0,
                    "value"in i && (i.writable = !0),
                    Object.defineProperty(r, g(i.key), i)
                }
            }
            function g(r) {
                var n = function(r, n) {
                    if ("object" != h(r) || !r)
                        return r;
                    var o = r[d];
                    if (void 0 !== o) {
                        var i = o.call(r, n || "default");
                        if ("object" != h(i))
                            return i;
                        throw TypeError("@@toPrimitive must return a primitive value.")
                    }
                    return ("string" === n ? String : Number)(r)
                }(r, "string");
                return "symbol" == h(n) ? n : n + ""
            }
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.EventEmitter = void 0,
            o = function r() {
                var o, i;
                (function(r, o) {
                    if (!n(r, o))
                        throw TypeError("Cannot call a class as a function")
                }
                )(this, r),
                i = {},
                (o = g(o = "events"))in this ? Object.defineProperty(this, o, {
                    value: i,
                    enumerable: !0,
                    configurable: !0,
                    writable: !0
                }) : this[o] = i
            }
            ,
            i = [{
                key: "on",
                value: function(r, n) {
                    var o = this;
                    return Array.isArray(this.events[r]) || (this.events[r] = []),
                    this.events[r].push(n),
                    function() {
                        return o.removeListener(r, n)
                    }
                }
            }, {
                key: "off",
                value: function(r, n) {
                    return this.removeListener(r, n)
                }
            }, {
                key: "removeListener",
                value: function(r, n) {
                    if (Array.isArray(this.events[r])) {
                        var o, i = this.events[r].indexOf(n);
                        i > -1 && p(o = this.events[r]).call(o, i, 1)
                    }
                }
            }, {
                key: "removeAllListeners",
                value: function() {
                    var r = this;
                    v(this.events).forEach(function(n) {
                        var o;
                        return null === (o = r.events[n]) || void 0 === o ? void 0 : p(o).call(o, 0, r.events[n].length)
                    })
                }
            }, {
                key: "emit",
                value: function(r) {
                    for (var n, o = this, i = arguments.length, u = Array(i > 1 ? i - 1 : 0), c = 1; c < i; c++)
                        u[c - 1] = arguments[c];
                    Array.isArray(this.events[r]) && ((function(r) {
                        if (Array.isArray(r))
                            return y(r)
                    }
                    )(n = this.events[r]) || function(r) {
                        if (void 0 !== a && null != f(r) || null != r["@@iterator"])
                            return l(r)
                    }(n) || function(r, n) {
                        if (r) {
                            if ("string" == typeof r)
                                return y(r, void 0);
                            var o, i = s(o = ({}).toString.call(r)).call(o, 8, -1);
                            return "Object" === i && r.constructor && (i = r.constructor.name),
                            "Map" === i || "Set" === i ? l(r) : "Arguments" === i || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i) ? y(r, void 0) : void 0
                        }
                    }(n) || function() {
                        throw TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")
                    }()).forEach(function(r) {
                        return r.apply(o, u)
                    })
                }
            }, {
                key: "once",
                value: function(r, n) {
                    var o = this
                      , i = this.on(r, function() {
                        i();
                        for (var r = arguments.length, u = Array(r), a = 0; a < r; a++)
                            u[a] = arguments[a];
                        n.apply(o, u)
                    });
                    return i
                }
            }],
            m(o.prototype, i),
            u && m(o, u),
            Object.defineProperty(o, "prototype", {
                writable: !1
            }),
            r.EventEmitter = o
        }
    })
      , nN = u({
        "node_modules/core-js-pure/internals/array-sort.js": function(r, n) {
            var o = eC()
              , i = Math.floor
              , u = function(r, n) {
                var a = r.length;
                if (a < 8)
                    for (var c, s, l = 1; l < a; ) {
                        for (s = l,
                        c = r[l]; s && n(r[s - 1], c) > 0; )
                            r[s] = r[--s];
                        s !== l++ && (r[s] = c)
                    }
                else
                    for (var f = i(a / 2), d = u(o(r, 0, f), n), p = u(o(r, f), n), v = d.length, h = p.length, y = 0, m = 0; y < v || m < h; )
                        r[y + m] = y < v && m < h ? 0 >= n(d[y], p[m]) ? d[y++] : p[m++] : y < v ? d[y++] : p[m++];
                return r
            };
            n.exports = u
        }
    })
      , nD = u({
        "node_modules/core-js-pure/internals/array-method-is-strict.js": function(r, n) {
            var o = c();
            n.exports = function(r, n) {
                var i = [][r];
                return !!i && o(function() {
                    i.call(null, n || function() {
                        return 1
                    }
                    , 1)
                })
            }
        }
    })
      , nB = u({
        "node_modules/core-js-pure/internals/environment-ff-version.js": function(r, n) {
            var o = k().match(/firefox\/(\d+)/i);
            n.exports = !!o && +o[1]
        }
    })
      , nU = u({
        "node_modules/core-js-pure/internals/environment-is-ie-or-edge.js": function(r, n) {
            var o = k();
            n.exports = /MSIE|Trident/.test(o)
        }
    })
      , nF = u({
        "node_modules/core-js-pure/internals/environment-webkit-version.js": function(r, n) {
            var o = k().match(/AppleWebKit\/(\d+)\./);
            n.exports = !!o && +o[1]
        }
    })
      , nq = u({
        "node_modules/core-js-pure/modules/es.array.sort.js": function() {
            var r = et()
              , n = f()
              , o = R()
              , i = F()
              , u = eu()
              , a = r9()
              , s = eg()
              , l = c()
              , d = nN()
              , p = nD()
              , v = nB()
              , h = nU()
              , y = S()
              , m = nF()
              , g = []
              , b = n(g.sort)
              , j = n(g.push)
              , w = l(function() {
                g.sort(void 0)
            })
              , x = l(function() {
                g.sort(null)
            })
              , _ = p("sort")
              , E = !l(function() {
                if (y)
                    return y < 70;
                if (!(v && v > 3)) {
                    if (h)
                        return !0;
                    if (m)
                        return m < 603;
                    var r, n, o, i, u = "";
                    for (r = 65; r < 76; r++) {
                        switch (n = String.fromCharCode(r),
                        r) {
                        case 66:
                        case 69:
                        case 70:
                        case 72:
                            o = 3;
                            break;
                        case 68:
                        case 71:
                            o = 4;
                            break;
                        default:
                            o = 2
                        }
                        for (i = 0; i < 47; i++)
                            g.push({
                                k: n + i,
                                v: o
                            })
                    }
                    for (g.sort(function(r, n) {
                        return n.v - r.v
                    }),
                    i = 0; i < g.length; i++)
                        n = g[i].k.charAt(0),
                        u.charAt(u.length - 1) !== n && (u += n);
                    return "DGBEFHACIJK" !== u
                }
            });
            r({
                target: "Array",
                proto: !0,
                forced: w || !x || !_ || !E
            }, {
                sort: function(r) {
                    void 0 !== r && o(r);
                    var n = i(this);
                    if (E)
                        return void 0 === r ? b(n) : b(n, r);
                    var c, l, f = [], p = u(n);
                    for (l = 0; l < p; l++)
                        l in n && j(f, n[l]);
                    for (d(f, function(n, o) {
                        return void 0 === o ? -1 : void 0 === n ? 1 : void 0 !== r ? +r(n, o) || 0 : s(n) > s(o) ? 1 : -1
                    }),
                    c = u(f),
                    l = 0; l < c; )
                        n[l] = f[l++];
                    for (; l < p; )
                        a(n, l++);
                    return n
                }
            })
        }
    })
      , nH = u({
        "node_modules/core-js-pure/es/array/virtual/sort.js": function(r, n) {
            nq(),
            n.exports = tI()("Array", "sort")
        }
    })
      , nz = u({
        "node_modules/core-js-pure/es/instance/sort.js": function(r, n) {
            var o = T()
              , i = nH()
              , u = Array.prototype;
            n.exports = function(r) {
                var n = r.sort;
                return r === u || o(u, r) && n === u.sort ? i : n
            }
        }
    })
      , nV = u({
        "node_modules/core-js-pure/stable/instance/sort.js": function(r, n) {
            n.exports = nz()
        }
    })
      , nG = u({
        "src/common/IntersectionObserver.ts": function(r) {
            var n = tw()
              , o = tO()
              , i = r$()
              , u = tM()
              , a = r2()
              , c = nV()
              , s = nn();
            function l(r) {
                return (l = "function" == typeof n && "symbol" == typeof o ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof n && r.constructor === n && r !== n.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            function() {
                if ("object" === ("undefined" == typeof window ? "undefined" : l(window))) {
                    if ("IntersectionObserver"in window && "IntersectionObserverEntry"in window && "intersectionRatio"in window.IntersectionObserverEntry.prototype)
                        "isIntersecting"in window.IntersectionObserverEntry.prototype || Object.defineProperty(window.IntersectionObserverEntry.prototype, "isIntersecting", {
                            get: function() {
                                return this.intersectionRatio > 0
                            }
                        });
                    else {
                        var r = function(r) {
                            for (var n = window.document, o = d(n); o; )
                                o = d(n = o.ownerDocument);
                            return n
                        }()
                          , n = []
                          , o = null
                          , f = null;
                        v.prototype.THROTTLE_TIMEOUT = 100,
                        v.prototype.POLL_INTERVAL = null,
                        v.prototype.USE_MUTATION_OBSERVER = !0,
                        v._setupCrossOriginUpdater = function() {
                            return o || (o = function(r, o) {
                                f = r && o ? b(r, o) : {
                                    top: 0,
                                    bottom: 0,
                                    left: 0,
                                    right: 0,
                                    width: 0,
                                    height: 0
                                },
                                n.forEach(function(r) {
                                    r._checkForIntersections()
                                })
                            }
                            ),
                            o
                        }
                        ,
                        v._resetCrossOriginUpdater = function() {
                            o = null,
                            f = null
                        }
                        ,
                        v.prototype.observe = function(r) {
                            if (!this._observationTargets.some(function(n) {
                                return n.element == r
                            })) {
                                if (!r || 1 != r.nodeType)
                                    throw Error("target must be an Element");
                                this._registerInstance(),
                                this._observationTargets.push({
                                    element: r,
                                    entry: null
                                }),
                                this._monitorIntersections(r.ownerDocument),
                                this._checkForIntersections()
                            }
                        }
                        ,
                        v.prototype.unobserve = function(r) {
                            var n;
                            this._observationTargets = u(n = this._observationTargets).call(n, function(n) {
                                return n.element != r
                            }),
                            this._unmonitorIntersections(r.ownerDocument),
                            0 == this._observationTargets.length && this._unregisterInstance()
                        }
                        ,
                        v.prototype.disconnect = function() {
                            this._observationTargets = [],
                            this._unmonitorAllIntersections(),
                            this._unregisterInstance()
                        }
                        ,
                        v.prototype.takeRecords = function() {
                            var r, n = a(r = this._queuedEntries).call(r);
                            return this._queuedEntries = [],
                            n
                        }
                        ,
                        v.prototype._initThresholds = function(r) {
                            var n, o = r || [0];
                            return Array.isArray(o) || (o = [o]),
                            u(n = c(o).call(o)).call(n, function(r, n, o) {
                                if ("number" != typeof r || isNaN(r) || r < 0 || r > 1)
                                    throw Error("threshold must be a number between 0 and 1 inclusively");
                                return r !== o[n - 1]
                            })
                        }
                        ,
                        v.prototype._parseRootMargin = function(r) {
                            var n, o = i(n = (r || "0px").split(/\s+/)).call(n, function(r) {
                                var n = /^(-?\d*\.?\d+)(px|%)$/.exec(r);
                                if (!n)
                                    throw Error("rootMargin must be specified in pixels or percent");
                                return {
                                    value: parseFloat(n[1]),
                                    unit: n[2]
                                }
                            });
                            return o[1] = o[1] || o[0],
                            o[2] = o[2] || o[0],
                            o[3] = o[3] || o[1],
                            o
                        }
                        ,
                        v.prototype._monitorIntersections = function(n) {
                            var o = n.defaultView;
                            if (o && -1 == this._monitoringDocuments.indexOf(n)) {
                                var i = this._checkForIntersections
                                  , u = null
                                  , a = null;
                                if (this.POLL_INTERVAL ? u = o.setInterval(i, this.POLL_INTERVAL) : (h(o, "resize", i, !0),
                                h(n, "scroll", i, !0),
                                this.USE_MUTATION_OBSERVER && "MutationObserver"in o && (a = new o.MutationObserver(i)).observe(n, {
                                    attributes: !0,
                                    childList: !0,
                                    characterData: !0,
                                    subtree: !0
                                })),
                                this._monitoringDocuments.push(n),
                                this._monitoringUnsubscribes.push(function() {
                                    var r = n.defaultView;
                                    r && (u && r.clearInterval(u),
                                    y(r, "resize", i, !0)),
                                    y(n, "scroll", i, !0),
                                    a && a.disconnect()
                                }),
                                n != (this.root && (this.root.ownerDocument || this.root) || r)) {
                                    var c = d(n);
                                    c && this._monitorIntersections(c.ownerDocument)
                                }
                            }
                        }
                        ,
                        v.prototype._unmonitorIntersections = function(n) {
                            var o, i, u = this._monitoringDocuments.indexOf(n);
                            if (-1 != u) {
                                var a = this.root && (this.root.ownerDocument || this.root) || r;
                                if (!this._observationTargets.some(function(r) {
                                    var o = r.element.ownerDocument;
                                    if (o == n)
                                        return !0;
                                    for (; o && o != a; ) {
                                        var i = d(o);
                                        if ((o = i && i.ownerDocument) == n)
                                            return !0
                                    }
                                    return !1
                                })) {
                                    var c = this._monitoringUnsubscribes[u];
                                    if (s(o = this._monitoringDocuments).call(o, u, 1),
                                    s(i = this._monitoringUnsubscribes).call(i, u, 1),
                                    c(),
                                    n != a) {
                                        var l = d(n);
                                        l && this._unmonitorIntersections(l.ownerDocument)
                                    }
                                }
                            }
                        }
                        ,
                        v.prototype._unmonitorAllIntersections = function() {
                            var r, n = a(r = this._monitoringUnsubscribes).call(r, 0);
                            this._monitoringDocuments.length = 0,
                            this._monitoringUnsubscribes.length = 0;
                            for (var o = 0; o < n.length; o++)
                                n[o]()
                        }
                        ,
                        v.prototype._checkForIntersections = function() {
                            if (this.root || !o || f) {
                                var r = this._rootIsInDom()
                                  , n = r ? this._getRootRect() : {
                                    top: 0,
                                    bottom: 0,
                                    left: 0,
                                    right: 0,
                                    width: 0,
                                    height: 0
                                };
                                this._observationTargets.forEach(function(i) {
                                    var u = i.element
                                      , a = m(u)
                                      , c = this._rootContainsTarget(u)
                                      , s = i.entry
                                      , l = r && c && this._computeTargetAndRootIntersection(u, a, n)
                                      , f = null;
                                    this._rootContainsTarget(u) ? o && !this.root || (f = n) : f = {
                                        top: 0,
                                        bottom: 0,
                                        left: 0,
                                        right: 0,
                                        width: 0,
                                        height: 0
                                    };
                                    var d = i.entry = new p({
                                        time: window.performance && performance.now && performance.now(),
                                        target: u,
                                        boundingClientRect: a,
                                        rootBounds: f,
                                        intersectionRect: l
                                    });
                                    s ? r && c ? this._hasCrossedThreshold(s, d) && this._queuedEntries.push(d) : s && s.isIntersecting && this._queuedEntries.push(d) : this._queuedEntries.push(d)
                                }, this),
                                this._queuedEntries.length && this._callback(this.takeRecords(), this)
                            }
                        }
                        ,
                        v.prototype._computeTargetAndRootIntersection = function(n, i, u) {
                            if ("none" != window.getComputedStyle(n).display) {
                                for (var a = i, c = w(n), s = !1; !s && c; ) {
                                    var l = null
                                      , d = 1 == c.nodeType ? window.getComputedStyle(c) : {};
                                    if ("none" == d.display)
                                        return null;
                                    if (c == this.root || 9 == c.nodeType) {
                                        if (s = !0,
                                        c == this.root || c == r)
                                            o && !this.root ? f && (0 != f.width || 0 != f.height) ? l = f : (c = null,
                                            l = null,
                                            a = null) : l = u;
                                        else {
                                            var p = w(c)
                                              , v = p && m(p)
                                              , h = p && this._computeTargetAndRootIntersection(p, v, u);
                                            v && h ? (c = p,
                                            l = b(v, h)) : (c = null,
                                            a = null)
                                        }
                                    } else {
                                        var y = c.ownerDocument;
                                        c != y.body && c != y.documentElement && "visible" != d.overflow && (l = m(c))
                                    }
                                    if (l && (a = function(r, n) {
                                        var o = Math.max(r.top, n.top)
                                          , i = Math.min(r.bottom, n.bottom)
                                          , u = Math.max(r.left, n.left)
                                          , a = Math.min(r.right, n.right)
                                          , c = a - u
                                          , s = i - o;
                                        return c >= 0 && s >= 0 && {
                                            top: o,
                                            bottom: i,
                                            left: u,
                                            right: a,
                                            width: c,
                                            height: s
                                        } || null
                                    }(l, a)),
                                    !a)
                                        break;
                                    c = c && w(c)
                                }
                                return a
                            }
                        }
                        ,
                        v.prototype._getRootRect = function() {
                            var n;
                            if (this.root && !x(this.root))
                                n = m(this.root);
                            else {
                                var o = x(this.root) ? this.root : r
                                  , i = o.documentElement
                                  , u = o.body;
                                n = {
                                    top: 0,
                                    left: 0,
                                    right: i.clientWidth || u.clientWidth,
                                    width: i.clientWidth || u.clientWidth,
                                    bottom: i.clientHeight || u.clientHeight,
                                    height: i.clientHeight || u.clientHeight
                                }
                            }
                            return this._expandRectByRootMargin(n)
                        }
                        ,
                        v.prototype._expandRectByRootMargin = function(r) {
                            var n, o = i(n = this._rootMarginValues).call(n, function(n, o) {
                                return "px" == n.unit ? n.value : n.value * (o % 2 ? r.width : r.height) / 100
                            }), u = {
                                top: r.top - o[0],
                                right: r.right + o[1],
                                bottom: r.bottom + o[2],
                                left: r.left - o[3]
                            };
                            return u.width = u.right - u.left,
                            u.height = u.bottom - u.top,
                            u
                        }
                        ,
                        v.prototype._hasCrossedThreshold = function(r, n) {
                            var o = r && r.isIntersecting ? r.intersectionRatio || 0 : -1
                              , i = n.isIntersecting ? n.intersectionRatio || 0 : -1;
                            if (o !== i)
                                for (var u = 0; u < this.thresholds.length; u++) {
                                    var a = this.thresholds[u];
                                    if (a == o || a == i || a < o != a < i)
                                        return !0
                                }
                        }
                        ,
                        v.prototype._rootIsInDom = function() {
                            return !this.root || j(r, this.root)
                        }
                        ,
                        v.prototype._rootContainsTarget = function(n) {
                            var o = this.root && (this.root.ownerDocument || this.root) || r;
                            return j(o, n) && (!this.root || o == n.ownerDocument)
                        }
                        ,
                        v.prototype._registerInstance = function() {
                            0 > n.indexOf(this) && n.push(this)
                        }
                        ,
                        v.prototype._unregisterInstance = function() {
                            var r = n.indexOf(this);
                            -1 != r && s(n).call(n, r, 1)
                        }
                        ,
                        window.IntersectionObserver = v,
                        window.IntersectionObserverEntry = p
                    }
                }
                function d(r) {
                    try {
                        return r.defaultView && r.defaultView.frameElement || null
                    } catch (r) {
                        return null
                    }
                }
                function p(r) {
                    this.time = r.time,
                    this.target = r.target,
                    this.rootBounds = g(r.rootBounds),
                    this.boundingClientRect = g(r.boundingClientRect),
                    this.intersectionRect = g(r.intersectionRect || {
                        top: 0,
                        bottom: 0,
                        left: 0,
                        right: 0,
                        width: 0,
                        height: 0
                    }),
                    this.isIntersecting = !!r.intersectionRect;
                    var n = this.boundingClientRect
                      , o = n.width * n.height
                      , i = this.intersectionRect
                      , u = i.width * i.height;
                    this.intersectionRatio = o ? Number((u / o).toFixed(4)) : +!!this.isIntersecting
                }
                function v(r, n) {
                    var o, u, a, c, s = n || {};
                    if ("function" != typeof r)
                        throw Error("callback must be a function");
                    if (s.root && 1 != s.root.nodeType && 9 != s.root.nodeType)
                        throw Error("root must be a Document or Element");
                    this._checkForIntersections = (o = this._checkForIntersections.bind(this),
                    u = this.THROTTLE_TIMEOUT,
                    a = null,
                    function() {
                        a || (a = setTimeout(function() {
                            o(),
                            a = null
                        }, u))
                    }
                    ),
                    this._callback = r,
                    this._observationTargets = [],
                    this._queuedEntries = [],
                    this._rootMarginValues = this._parseRootMargin(s.rootMargin),
                    this.thresholds = this._initThresholds(s.threshold),
                    this.root = s.root || null,
                    this.rootMargin = i(c = this._rootMarginValues).call(c, function(r) {
                        return r.value + r.unit
                    }).join(" "),
                    this._monitoringDocuments = [],
                    this._monitoringUnsubscribes = []
                }
                function h(r, n, o, i) {
                    "function" == typeof r.addEventListener ? r.addEventListener(n, o, i || !1) : "function" == typeof r.attachEvent && r.attachEvent("on" + n, o)
                }
                function y(r, n, o, i) {
                    "function" == typeof r.removeEventListener ? r.removeEventListener(n, o, i || !1) : "function" == typeof r.detatchEvent && r.detatchEvent("on" + n, o)
                }
                function m(r) {
                    var n;
                    try {
                        n = r.getBoundingClientRect()
                    } catch (r) {}
                    return n ? (n.width && n.height || (n = {
                        top: n.top,
                        right: n.right,
                        bottom: n.bottom,
                        left: n.left,
                        width: n.right - n.left,
                        height: n.bottom - n.top
                    }),
                    n) : {
                        top: 0,
                        bottom: 0,
                        left: 0,
                        right: 0,
                        width: 0,
                        height: 0
                    }
                }
                function g(r) {
                    return !r || "x"in r ? r : {
                        top: r.top,
                        y: r.top,
                        bottom: r.bottom,
                        left: r.left,
                        x: r.left,
                        right: r.right,
                        width: r.width,
                        height: r.height
                    }
                }
                function b(r, n) {
                    var o = n.top - r.top
                      , i = n.left - r.left;
                    return {
                        top: o,
                        left: i,
                        height: n.height,
                        width: n.width,
                        bottom: o + n.height,
                        right: i + n.width
                    }
                }
                function j(r, n) {
                    for (var o = n; o; ) {
                        if (o == r)
                            return !0;
                        o = w(o)
                    }
                    return !1
                }
                function w(n) {
                    var o = n.parentNode;
                    return 9 == n.nodeType && n != r ? d(n) : (o && o.assignedSlot && (o = o.assignedSlot.parentNode),
                    o && 11 == o.nodeType && o.host ? o.host : o)
                }
                function x(r) {
                    return r && 9 === r.nodeType
                }
            }()
        }
    })
      , nJ = u({
        "src/common/MutationObserver.ts": function(r) {
            var n = nn();
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            window.MutationObserver = window.MutationObserver || function(r) {
                function o(r) {
                    this._watched = [],
                    this._listener = r
                }
                function i(n) {
                    var o = {
                        type: null,
                        target: null,
                        addedNodes: [],
                        removedNodes: [],
                        previousSibling: null,
                        nextSibling: null,
                        attributeName: null,
                        attributeNamespace: null,
                        oldValue: null
                    };
                    for (var i in n)
                        o[i] !== r && n[i] !== r && (o[i] = n[i]);
                    return o
                }
                o._period = 30,
                o.prototype = {
                    observe: function(u, a) {
                        for (var l, f, h = {
                            attr: !!(a.attributes || a.attributeFilter || a.attributeOldValue),
                            kids: !!a.childList,
                            descendents: !!a.subtree,
                            charData: !(!a.characterData && !a.characterDataOldValue)
                        }, y = this._watched, m = 0; m < y.length; m++)
                            y[m].tar === u && n(y).call(y, m, 1);
                        a.attributeFilter && (h.afilter = p(a.attributeFilter, function(r, n) {
                            return r[n] = !0,
                            r
                        }, {})),
                        y.push({
                            tar: u,
                            fn: (l = s(u, h),
                            function(n) {
                                var o, a = n.length;
                                h.charData && 3 === u.nodeType && u.nodeValue !== l.charData && n.push(new i({
                                    type: "characterData",
                                    target: u,
                                    oldValue: l.charData
                                })),
                                h.attr && l.attr && c(n, u, l.attr, h.afilter),
                                (h.kids || h.descendents) && (o = function(n, o, u, a) {
                                    var s;
                                    function l(r, o, u, s, l) {
                                        for (var d, p, v, h = r.length - 1, y = -~((h - l) / 2); v = r.pop(); )
                                            d = u[v.i],
                                            p = s[v.j],
                                            a.kids && y && Math.abs(v.i - v.j) >= h && (n.push(i({
                                                type: "childList",
                                                target: o,
                                                addedNodes: [d],
                                                removedNodes: [d],
                                                nextSibling: d.nextSibling,
                                                previousSibling: d.previousSibling
                                            })),
                                            y--),
                                            a.attr && p.attr && c(n, d, p.attr, a.afilter),
                                            a.charData && 3 === d.nodeType && d.nodeValue !== p.charData && n.push(i({
                                                type: "characterData",
                                                target: d,
                                                oldValue: p.charData
                                            })),
                                            a.descendents && f(d, p)
                                    }
                                    function f(o, u) {
                                        for (var p, h, y, m, g, b, j, w = o.childNodes, x = u.kids, _ = w.length, E = x ? x.length : 0, O = 0, T = 0, k = 0; T < _ || k < E; )
                                            (b = w[T]) === (j = (g = x[k]) && g.node) ? (a.attr && g.attr && c(n, b, g.attr, a.afilter),
                                            a.charData && g.charData !== r && b.nodeValue !== g.charData && n.push(i({
                                                type: "characterData",
                                                target: b,
                                                oldValue: g.charData
                                            })),
                                            h && l(h, o, w, x, O),
                                            a.descendents && (b.childNodes.length || g.kids && g.kids.length) && f(b, g),
                                            T++,
                                            k++) : (s = !0,
                                            p || (p = {},
                                            h = []),
                                            b && (p[y = d(b)] || (p[y] = !0,
                                            -1 === (m = v(x, b, k, "node")) ? a.kids && (n.push(i({
                                                type: "childList",
                                                target: o,
                                                addedNodes: [b],
                                                nextSibling: b.nextSibling,
                                                previousSibling: b.previousSibling
                                            })),
                                            O++) : h.push({
                                                i: T,
                                                j: m
                                            })),
                                            T++),
                                            j && j !== w[T] && (p[y = d(j)] || (p[y] = !0,
                                            -1 === (m = v(w, j, T)) ? a.kids && (n.push(i({
                                                type: "childList",
                                                target: u.node,
                                                removedNodes: [j],
                                                nextSibling: x[k + 1],
                                                previousSibling: x[k - 1]
                                            })),
                                            O--) : h.push({
                                                i: m,
                                                j: k
                                            })),
                                            k++));
                                        h && l(h, o, w, x, O)
                                    }
                                    return f(o, u),
                                    s
                                }(n, u, l, h)),
                                (o || n.length !== a) && (l = s(u, h))
                            }
                            )
                        }),
                        this._timeout || (f = this,
                        function r() {
                            var n = f.takeRecords();
                            n.length && f._listener(n, f),
                            f._timeout = setTimeout(r, o._period)
                        }())
                    },
                    takeRecords: function() {
                        for (var r = [], n = this._watched, o = 0; o < n.length; o++)
                            n[o].fn(r);
                        return r
                    },
                    disconnect: function() {
                        this._watched = [],
                        clearTimeout(this._timeout),
                        this._timeout = null
                    }
                };
                var u = document.createElement("i");
                u.style.top = 0;
                var a = (u = "null" != u.attributes.style.value) ? function(r, n) {
                    return n.value
                }
                : function(r, n) {
                    return "style" !== n.name ? n.value : r.style.cssText
                }
                ;
                function c(n, o, u, c) {
                    for (var s, l, f = {}, d = o.attributes, p = d.length; p--; )
                        l = (s = d[p]).name,
                        c && c[l] === r || (a(o, s) !== u[l] && n.push(i({
                            type: "attributes",
                            target: o,
                            attributeName: l,
                            oldValue: u[l],
                            attributeNamespace: s.namespaceURI
                        })),
                        f[l] = !0);
                    for (l in u)
                        f[l] || n.push(i({
                            target: o,
                            type: "attributes",
                            attributeName: l,
                            oldValue: u[l]
                        }))
                }
                function s(r, n) {
                    var o = !0;
                    return function r(i) {
                        var u = {
                            node: i
                        };
                        return n.charData && (3 === i.nodeType || 8 === i.nodeType) ? u.charData = i.nodeValue : (n.attr && o && 1 === i.nodeType && (u.attr = p(i.attributes, function(r, o) {
                            return n.afilter && !n.afilter[o.name] || (r[o.name] = a(i, o)),
                            r
                        }, {})),
                        o && (n.kids || n.charData || n.attr && n.descendents) && (u.kids = function(r, n) {
                            for (var o = [], i = 0; i < r.length; i++)
                                o[i] = n(r[i], i, r);
                            return o
                        }(i.childNodes, r)),
                        o = n.descendents),
                        u
                    }(r)
                }
                var l = 1
                  , f = "mo_id";
                function d(r) {
                    try {
                        return r.id || (r[f] = r[f] || l++)
                    } catch (n) {
                        try {
                            return r.nodeValue
                        } catch (r) {
                            return l++
                        }
                    }
                }
                function p(r, n, o) {
                    for (var i = 0; i < r.length; i++)
                        o = n(o, r[i], i, r);
                    return o
                }
                function v(r, n, o, i) {
                    for (; o < r.length; o++)
                        if ((i ? r[o][i] : r[o]) === n)
                            return o;
                    return -1
                }
                return o
            }(void 0)
        }
    })
      , nK = u({
        "src/common/index.ts": function(r) {
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            Object.defineProperty(r, "EventEmitter", {
                enumerable: !0,
                get: function() {
                    return i.EventEmitter
                }
            }),
            Object.defineProperty(r, "LifecycleEvent", {
                enumerable: !0,
                get: function() {
                    return u.LifecycleEvent
                }
            }),
            Object.defineProperty(r, "Log", {
                enumerable: !0,
                get: function() {
                    return o.default
                }
            }),
            Object.defineProperty(r, "STORAGE_KEY", {
                enumerable: !0,
                get: function() {
                    return u.STORAGE_KEY
                }
            }),
            Object.defineProperty(r, "asyncThrowError", {
                enumerable: !0,
                get: function() {
                    return a.asyncThrowError
                }
            }),
            Object.defineProperty(r, "cookie", {
                enumerable: !0,
                get: function() {
                    return c.cookie
                }
            });
            var n, o = (n = nL()) && n.__esModule ? n : {
                default: n
            }, i = nM(), u = nI(), a = nd(), c = nl();
            nG(),
            nJ()
        }
    })
      , nW = u({
        "src/collect/click/index.ts": function(r) {
            var o = tw()
              , i = tO()
              , u = tX()
              , a = tS()
              , c = tC()
              , s = tM()
              , l = tB()
              , f = tH()
              , d = t2()
              , p = tG()
              , v = tZ();
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.Click = void 0,
            r.default = function(r) {
                for (var n, o, i = arguments.length, a = Array(i > 1 ? i - 1 : 0), c = 1; c < i; c++)
                    a[c - 1] = arguments[c];
                var s, l = x({}, a)[0];
                return null === (n = null == l || null === (o = l.collect) || void 0 === o || null === (o = o.click) || void 0 === o ? void 0 : o.enable) || void 0 === n || n ? function(r, n, o) {
                    if (_())
                        return u.apply(null, arguments);
                    var i = [null];
                    i.push.apply(i, n);
                    var a = new (r.bind.apply(r, i));
                    return o && O(a, o.prototype),
                    a
                }(S, v(s = [r]).call(s, a)) : null
            }
            ;
            var h, y = (h = nR()) && h.__esModule ? h : {
                default: h
            }, m = nI(), g = nK(), b = nd();
            function j(r) {
                return (j = "function" == typeof o && "symbol" == typeof i ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof o && r.constructor === o && r !== o.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            function w(r, n) {
                var o = a(r);
                if (c) {
                    var i = c(r);
                    n && (i = s(i).call(i, function(n) {
                        return l(r, n).enumerable
                    })),
                    o.push.apply(o, i)
                }
                return o
            }
            function x(r) {
                for (var n = 1; n < arguments.length; n++) {
                    var o = null != arguments[n] ? arguments[n] : {};
                    n % 2 ? w(Object(o), !0).forEach(function(n) {
                        T(r, n, o[n])
                    }) : f ? Object.defineProperties(r, f(o)) : w(Object(o)).forEach(function(n) {
                        Object.defineProperty(r, n, l(o, n))
                    })
                }
                return r
            }
            function _() {
                try {
                    var r = !Boolean.prototype.valueOf.call(u(Boolean, [], function() {}))
                } catch (r) {}
                return (_ = function() {
                    return !!r
                }
                )()
            }
            function E(r) {
                return (E = Object.setPrototypeOf ? d.bind() : function(r) {
                    return r.__proto__ || d(r)
                }
                )(r)
            }
            function O(r, n) {
                return (O = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(r, n) {
                    return r.__proto__ = n,
                    r
                }
                )(r, n)
            }
            function T(r, n, o) {
                return (n = k(n))in r ? Object.defineProperty(r, n, {
                    value: o,
                    enumerable: !0,
                    configurable: !0,
                    writable: !0
                }) : r[n] = o,
                r
            }
            function k(r) {
                var n = function(r, n) {
                    if ("object" != j(r) || !r)
                        return r;
                    var o = r[p];
                    if (void 0 !== o) {
                        var i = o.call(r, n || "default");
                        if ("object" != j(i))
                            return i;
                        throw TypeError("@@toPrimitive must return a primitive value.")
                    }
                    return ("string" === n ? String : Number)(r)
                }(r, "string");
                return "symbol" == j(n) ? n : n + ""
            }
            var S = r.Click = function(r) {
                var o;
                function i(r, o) {
                    var c, s, l;
                    return function(r, o) {
                        if (!n(r, o))
                            throw TypeError("Cannot call a class as a function")
                    }(this, i),
                    T((s = i,
                    l = [{
                        dialogAlias: o.dialogAlias
                    }],
                    s = E(s),
                    c = function(r, n) {
                        if (n && ("object" == j(n) || "function" == typeof n))
                            return n;
                        if (void 0 !== n)
                            throw TypeError("Derived constructors may only return object or undefined");
                        return function(r) {
                            if (void 0 === r)
                                throw ReferenceError("this hasn't been initialised - super() hasn't been called");
                            return r
                        }(r)
                    }(this, _() ? u(s, l || [], E(this).constructor) : s.apply(this, l))), "config", {}),
                    T(c, "trackc", function(r) {
                        var n = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {};
                        try {
                            var o, i, u, s = r.target || r.srcElement, l = c.xpath(s), f = l.index, d = l.xpath, p = l.dataInfo, h = l.scm, y = l.elemId, j = l.ext;
                            if (!d)
                                return;
                            var w, _ = (0,
                            b.setEventSeq)(), E = {
                                type: m.ReportEventType.click,
                                data_info: n || {},
                                eventSeq: _,
                                pgRefObj: {
                                    scm: void 0 === h ? {} : h,
                                    elemId: (void 0 === y ? "" : y) || v(o = "".concat(m.AUTOTRACK_KEY)).call(o, d),
                                    ext: void 0 === j ? {} : j
                                }
                            };
                            E.xpath = d,
                            a(p).length && (E.data_info = x(x({}, E.data_info), p || {})),
                            f > -1 && (E.data_info && (E.data_info.index = f),
                            null != E && null !== (w = E.pgRefObj) && void 0 !== w && w.ext && (E.pgRefObj.ext.index = f)),
                            E.data_info && !E.data_info.text && (E.data_info.text = c.getTextByTextNode(s)),
                            E.pgRefObj && (null === (i = E.pgRefObj) || void 0 === i || !i.ext.text) && E.data_info && (E.pgRefObj.ext.text = E.data_info.text),
                            c.info("".concat(m.ReportEventType.click, " 事件上报数据: "), E),
                            c.report({
                                ev_type: m.ReportEventType.click,
                                payload: x({}, E)
                            });
                            var O = null === (u = c.client) || void 0 === u ? void 0 : u.getPgRefByElem(s)
                              , T = c.attr(s, "data-tlg-sendpgref-ignore");
                            if (T && "true" === T)
                                return;
                            (0,
                            b.isInvalidPgRef)(O) ? c.client.sendPgRefToApp(m.PGREF_DEFAULT_APPCODE) : c.client.sendPgRefToApp(O)
                        } catch (r) {
                            (0,
                            g.asyncThrowError)(r)
                        }
                    }),
                    c.config = x({}, o),
                    c.type = "click",
                    c.client = r,
                    c.init(),
                    c.info("click捕获 初始化"),
                    c
                }
                return function(r, n) {
                    if ("function" != typeof n && null !== n)
                        throw TypeError("Super expression must either be null or a function");
                    r.prototype = Object.create(n && n.prototype, {
                        constructor: {
                            value: r,
                            writable: !0,
                            configurable: !0
                        }
                    }),
                    Object.defineProperty(r, "prototype", {
                        writable: !1
                    }),
                    n && O(r, n)
                }(i, r),
                o = [{
                    key: "report",
                    value: function(r) {
                        this.client.report(r)
                    }
                }, {
                    key: "init",
                    value: function() {
                        this.info("开始监听 click 事件");
                        try {
                            (0,
                            b.removeEventListener)(document.body, "click", this.trackc),
                            (0,
                            b.addEventListener)(document.body, "click", this.trackc)
                        } catch (r) {
                            (0,
                            g.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "info",
                    value: function() {
                        for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                            i[u] = arguments[u];
                        return (n = this.client.logs).info.apply(n, v(r = ["Click"]).call(r, i))
                    }
                }, {
                    key: "error",
                    value: function() {
                        for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                            i[u] = arguments[u];
                        return (n = this.client.logs).error.apply(n, v(r = ["Click"]).call(r, i))
                    }
                }, {
                    key: "destroy",
                    value: function() {
                        try {
                            (0,
                            b.removeEventListener)(document.body, "click", this.trackc),
                            this.info("click 事件 destroy")
                        } catch (r) {
                            (0,
                            g.asyncThrowError)(r)
                        }
                    }
                }],
                function(r, n) {
                    for (var o = 0; o < n.length; o++) {
                        var i = n[o];
                        i.enumerable = i.enumerable || !1,
                        i.configurable = !0,
                        "value"in i && (i.writable = !0),
                        Object.defineProperty(r, k(i.key), i)
                    }
                }(i.prototype, o),
                Object.defineProperty(i, "prototype", {
                    writable: !1
                }),
                i
            }(y.default)
        }
    })
      , nY = u({
        "src/collect/alive/index.ts": function(r) {
            var o, i, u, a = tw(), c = tO(), s = tX(), l = tS(), f = tC(), d = tM(), p = tB(), v = tH(), h = tG(), y = tZ();
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.Alive = void 0,
            r.default = function(r) {
                for (var n, o, i = arguments.length, u = Array(i > 1 ? i - 1 : 0), a = 1; a < i; a++)
                    u[a - 1] = arguments[a];
                var c, l = E({}, u)[0];
                return null === (n = null == l || null === (o = l.collect) || void 0 === o || null === (o = o.alive) || void 0 === o ? void 0 : o.enable) || void 0 === n || n ? function(r, n, o) {
                    if (x())
                        return s.apply(null, arguments);
                    var i = [null];
                    i.push.apply(i, n);
                    var u = new (r.bind.apply(r, i));
                    return o && w(u, o.prototype),
                    u
                }(S, y(c = [r]).call(c, u)) : null
            }
            ;
            var m = nI()
              , g = nK()
              , b = nd();
            function j(r) {
                return (j = "function" == typeof a && "symbol" == typeof c ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof a && r.constructor === a && r !== a.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            function w(r, n) {
                return (w = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(r, n) {
                    return r.__proto__ = n,
                    r
                }
                )(r, n)
            }
            function x() {
                try {
                    var r = !Boolean.prototype.valueOf.call(s(Boolean, [], function() {}))
                } catch (r) {}
                return (x = function() {
                    return !!r
                }
                )()
            }
            function _(r, n) {
                var o = l(r);
                if (f) {
                    var i = f(r);
                    n && (i = d(i).call(i, function(n) {
                        return p(r, n).enumerable
                    })),
                    o.push.apply(o, i)
                }
                return o
            }
            function E(r) {
                for (var n = 1; n < arguments.length; n++) {
                    var o = null != arguments[n] ? arguments[n] : {};
                    n % 2 ? _(Object(o), !0).forEach(function(n) {
                        T(r, n, o[n])
                    }) : v ? Object.defineProperties(r, v(o)) : _(Object(o)).forEach(function(n) {
                        Object.defineProperty(r, n, p(o, n))
                    })
                }
                return r
            }
            function O(r, n) {
                for (var o = 0; o < n.length; o++) {
                    var i = n[o];
                    i.enumerable = i.enumerable || !1,
                    i.configurable = !0,
                    "value"in i && (i.writable = !0),
                    Object.defineProperty(r, k(i.key), i)
                }
            }
            function T(r, n, o) {
                return (n = k(n))in r ? Object.defineProperty(r, n, {
                    value: o,
                    enumerable: !0,
                    configurable: !0,
                    writable: !0
                }) : r[n] = o,
                r
            }
            function k(r) {
                var n = function(r, n) {
                    if ("object" != j(r) || !r)
                        return r;
                    var o = r[h];
                    if (void 0 !== o) {
                        var i = o.call(r, n || "default");
                        if ("object" != j(i))
                            return i;
                        throw TypeError("@@toPrimitive must return a primitive value.")
                    }
                    return ("string" === n ? String : Number)(r)
                }(r, "string");
                return "symbol" == j(n) ? n : n + ""
            }
            var S = (o = function r(o, i) {
                var u = this;
                (function(r, o) {
                    if (!n(r, o))
                        throw TypeError("Cannot call a class as a function")
                }
                )(this, r),
                T(this, "config", {}),
                T(this, "aliveHolder", null),
                T(this, "trackA3", function() {
                    (0,
                    b.now)() - u.client.lastSendTime > u.interval && (u.tracka("A000000003"),
                    u.unbindActive())
                }),
                T(this, "trackA2", function() {
                    (0,
                    b.now)() - u.client.lastSendTime > u.interval && (u.tracka("A000000002"),
                    u.unbindActive())
                }),
                T(this, "trackA4", function() {
                    (0,
                    b.now)() - u.client.lastSendTime > u.interval && (u.tracka("A000000004"),
                    u.unbindActive())
                }),
                T(this, "unBindLisener", function() {
                    "pc" === u.equipment ? ((0,
                    b.removeEventListener)(document, "mousemove", u.trackA3),
                    (0,
                    b.removeEventListener)(document, "scroll", u.trackA2)) : (0,
                    b.removeEventListener)(document, "touchmove", u.trackA4)
                }),
                this.config = E({}, i),
                this.client = o,
                this.equipment = (0,
                b.getEquipment)(),
                this.aliveHolder = null,
                this.type = "alive",
                this.interval = 6e4,
                this.init(),
                this.info("alive捕获 初始化")
            }
            ,
            i = [{
                key: "report",
                value: function(r) {
                    this.client.report(r)
                }
            }, {
                key: "init",
                value: function() {
                    this.info("开始监听 alive 事件"),
                    this.unBindLisener(),
                    this.alive()
                }
            }, {
                key: "unbindActive",
                value: function() {
                    this.unBindLisener(),
                    this.alive()
                }
            }, {
                key: "alive",
                value: function() {
                    var r = this;
                    this.aliveHolder = setTimeout(function() {
                        "pc" === r.equipment ? ((0,
                        b.addEventListener)(document, "mousemove", r.trackA3),
                        (0,
                        b.addEventListener)(document, "scroll", r.trackA2)) : (0,
                        b.addEventListener)(document, "touchmove", r.trackA4)
                    }, this.interval)
                }
            }, {
                key: "tracka",
                value: function(r) {
                    try {
                        var n = (0,
                        b.setEventSeq)()
                          , o = {
                            type: m.ReportEventType.alive,
                            traceCode: r,
                            eventSeq: n
                        };
                        this.info("".concat(m.ReportEventType.alive, " 事件上报数据: "), o),
                        this.report({
                            ev_type: m.ReportEventType.alive,
                            payload: E({}, o)
                        })
                    } catch (r) {
                        (0,
                        g.asyncThrowError)(r)
                    }
                }
            }, {
                key: "info",
                value: function() {
                    for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                        i[u] = arguments[u];
                    return (n = this.client.logs).info.apply(n, y(r = ["Alive"]).call(r, i))
                }
            }, {
                key: "error",
                value: function() {
                    for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                        i[u] = arguments[u];
                    return (n = this.client.logs).error.apply(n, y(r = ["Alive"]).call(r, i))
                }
            }, {
                key: "destroy",
                value: function() {
                    try {
                        this.aliveHolder = null,
                        this.unBindLisener(),
                        this.info("alive 事件 destroy")
                    } catch (r) {
                        (0,
                        g.asyncThrowError)(r)
                    }
                }
            }],
            O(o.prototype, i),
            u && O(o, u),
            Object.defineProperty(o, "prototype", {
                writable: !1
            }),
            r.Alive = o)
        }
    })
      , nX = u({
        "node_modules/core-js-pure/modules/es.array.find-index.js": function() {
            var r = et()
              , n = eH().findIndex
              , o = ti()
              , i = "findIndex"
              , u = !0;
            i in [] && [, ][i](function() {
                u = !1
            }),
            r({
                target: "Array",
                proto: !0,
                forced: u
            }, {
                findIndex: function(r) {
                    return n(this, r, arguments.length > 1 ? arguments[1] : void 0)
                }
            }),
            o(i)
        }
    })
      , nQ = u({
        "node_modules/core-js-pure/es/array/virtual/find-index.js": function(r, n) {
            nX(),
            n.exports = tI()("Array", "findIndex")
        }
    })
      , n$ = u({
        "node_modules/core-js-pure/es/instance/find-index.js": function(r, n) {
            var o = T()
              , i = nQ()
              , u = Array.prototype;
            n.exports = function(r) {
                var n = r.findIndex;
                return r === u || o(u, r) && n === u.findIndex ? i : n
            }
        }
    })
      , nZ = u({
        "node_modules/core-js-pure/stable/instance/find-index.js": function(r, n) {
            n.exports = n$()
        }
    })
      , n0 = u({
        "node_modules/core-js-pure/internals/object-assign.js": function(r, n) {
            var o = h()
              , i = f()
              , u = y()
              , a = c()
              , s = eE()
              , l = eI()
              , d = m()
              , p = F()
              , v = b()
              , g = Object.assign
              , j = Object.defineProperty
              , w = i([].concat);
            n.exports = !g || a(function() {
                if (o && 1 !== g({
                    b: 1
                }, g(j({}, "a", {
                    enumerable: !0,
                    get: function() {
                        j(this, "b", {
                            value: 3,
                            enumerable: !1
                        })
                    }
                }), {
                    b: 2
                })).b)
                    return !0;
                var r = {}
                  , n = {}
                  , i = Symbol("assign detection")
                  , u = "abcdefghijklmnopqrst";
                return r[i] = 7,
                u.split("").forEach(function(r) {
                    n[r] = r
                }),
                7 !== g({}, r)[i] || s(g({}, n)).join("") !== u
            }) ? function(r, n) {
                for (var i = p(r), a = arguments.length, c = 1, f = l.f, h = d.f; a > c; )
                    for (var y, m = v(arguments[c++]), g = f ? w(s(m), f(m)) : s(m), b = g.length, j = 0; b > j; )
                        y = g[j++],
                        o && !u(h, m, y) || (i[y] = m[y]);
                return i
            }
            : g
        }
    })
      , n1 = u({
        "node_modules/core-js-pure/modules/es.object.assign.js": function() {
            var r = et()
              , n = n0();
            r({
                target: "Object",
                stat: !0,
                arity: 2,
                forced: Object.assign !== n
            }, {
                assign: n
            })
        }
    })
      , n2 = u({
        "node_modules/core-js-pure/es/object/assign.js": function(r, n) {
            n1(),
            n.exports = E().Object.assign
        }
    })
      , n5 = u({
        "node_modules/core-js-pure/stable/object/assign.js": function(r, n) {
            n.exports = n2()
        }
    })
      , n3 = u({
        "src/collect/exposure/index.ts": function(r) {
            var o = tw()
              , i = tO()
              , u = tX()
              , a = tS()
              , c = tC()
              , s = tM()
              , l = tB()
              , f = tH()
              , d = t2()
              , p = tG()
              , v = tZ()
              , h = nn()
              , y = r8()
              , m = nZ()
              , g = n5();
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.Exposure = void 0,
            r.default = function(r) {
                for (var n, o, i = arguments.length, a = Array(i > 1 ? i - 1 : 0), c = 1; c < i; c++)
                    a[c - 1] = arguments[c];
                var s, l = T({}, a)[0];
                return null === (n = null == l || null === (o = l.collect) || void 0 === o || null === (o = o.exposure) || void 0 === o ? void 0 : o.enable) || void 0 === n || n ? function(r, n, o) {
                    if (k())
                        return u.apply(null, arguments);
                    var i = [null];
                    i.push.apply(i, n);
                    var a = new (r.bind.apply(r, i));
                    return o && P(a, o.prototype),
                    a
                }(I, v(s = [r]).call(s, a)) : null
            }
            ;
            var b, j = (b = nR()) && b.__esModule ? b : {
                default: b
            }, w = nI(), x = nK(), _ = nd();
            function E(r) {
                return (E = "function" == typeof o && "symbol" == typeof i ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof o && r.constructor === o && r !== o.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            function O(r, n) {
                var o = a(r);
                if (c) {
                    var i = c(r);
                    n && (i = s(i).call(i, function(n) {
                        return l(r, n).enumerable
                    })),
                    o.push.apply(o, i)
                }
                return o
            }
            function T(r) {
                for (var n = 1; n < arguments.length; n++) {
                    var o = null != arguments[n] ? arguments[n] : {};
                    n % 2 ? O(Object(o), !0).forEach(function(n) {
                        C(r, n, o[n])
                    }) : f ? Object.defineProperties(r, f(o)) : O(Object(o)).forEach(function(n) {
                        Object.defineProperty(r, n, l(o, n))
                    })
                }
                return r
            }
            function k() {
                try {
                    var r = !Boolean.prototype.valueOf.call(u(Boolean, [], function() {}))
                } catch (r) {}
                return (k = function() {
                    return !!r
                }
                )()
            }
            function S(r) {
                return (S = Object.setPrototypeOf ? d.bind() : function(r) {
                    return r.__proto__ || d(r)
                }
                )(r)
            }
            function P(r, n) {
                return (P = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(r, n) {
                    return r.__proto__ = n,
                    r
                }
                )(r, n)
            }
            function C(r, n, o) {
                return (n = A(n))in r ? Object.defineProperty(r, n, {
                    value: o,
                    enumerable: !0,
                    configurable: !0,
                    writable: !0
                }) : r[n] = o,
                r
            }
            function A(r) {
                var n = function(r, n) {
                    if ("object" != E(r) || !r)
                        return r;
                    var o = r[p];
                    if (void 0 !== o) {
                        var i = o.call(r, n || "default");
                        if ("object" != E(i))
                            return i;
                        throw TypeError("@@toPrimitive must return a primitive value.")
                    }
                    return ("string" === n ? String : Number)(r)
                }(r, "string");
                return "symbol" == E(n) ? n : n + ""
            }
            var I = r.Exposure = function(r) {
                var o;
                function i(r, o) {
                    var c, l, f;
                    return function(r, o) {
                        if (!n(r, o))
                            throw TypeError("Cannot call a class as a function")
                    }(this, i),
                    C((l = i,
                    f = [{
                        dialogAlias: o.dialogAlias
                    }],
                    l = S(l),
                    c = function(r, n) {
                        if (n && ("object" == E(n) || "function" == typeof n))
                            return n;
                        if (void 0 !== n)
                            throw TypeError("Derived constructors may only return object or undefined");
                        return function(r) {
                            if (void 0 === r)
                                throw ReferenceError("this hasn't been initialised - super() hasn't been called");
                            return r
                        }(r)
                    }(this, k() ? u(l, f || [], S(this).constructor) : l.apply(this, f))), "config", {}),
                    C(c, "multipleExposure", []),
                    C(c, "mutationObserverDynamic", []),
                    C(c, "intersectionObserver", []),
                    C(c, "EHolder", null),
                    C(c, "exposureCache", {}),
                    C(c, "initDefaultConfig", function() {
                        c.multipleExposure = [],
                        c.mutationObserverDynamic = [],
                        c.intersectionObserver = [],
                        c.mutationCallBackTimer = null,
                        c.EHolder = null,
                        c.timer = null,
                        c.timerGroups = {},
                        c.bindObserverTimer = {},
                        c.exposureCache = {
                            normal: {},
                            dynamic: {}
                        }
                    }),
                    C(c, "repeatedExposure", function(r) {
                        try {
                            var n, o = r.repeatedConfig, i = o.root, u = o.rootMargin, a = o.threshold;
                            if (!IntersectionObserver)
                                return;
                            var s = new IntersectionObserver(function(n) {
                                if (n[0].isIntersecting) {
                                    var o, i = c.xpath(n[0].target), u = i.index, a = i.xpath, s = i.dataInfo, l = i.scm, f = i.elemId, d = i.ext, p = (0,
                                    _.setEventSeq)(), h = {
                                        xpath: a,
                                        data_info: T(T({}, r.dataInfo), s),
                                        elem: n[0],
                                        eventSeq: p,
                                        pgRefObj: {
                                            scm: void 0 === l ? {} : l,
                                            elemId: (void 0 === f ? "" : f) || v(o = "".concat(w.AUTOTRACK_KEY)).call(o, a),
                                            ext: void 0 === d ? {} : d
                                        }
                                    };
                                    u > -1 && (h.index = u,
                                    h.pgRefObj.ext && (h.pgRefObj.ext.index = u),
                                    r.size && r.size > 0 && (h.index %= r.size)),
                                    c.tracke(h)
                                }
                            }
                            ,{
                                root: i || null,
                                rootMargin: void 0 === u ? 0 : u,
                                threshold: void 0 === a ? 1 : a
                            })
                              , l = c.xpath2selector(r.xpath)
                              , f = document.querySelector(l);
                            null == s || null === (n = s.observe) || void 0 === n || n.call(s, f),
                            c.intersectionObserver.push(s)
                        } catch (r) {
                            (0,
                            x.asyncThrowError)(r)
                        }
                    }),
                    C(c, "updateExposureAdapter", function() {
                        try {
                            var r = a(c.exposureCache.normal)
                              , n = a(c.exposureCache.dynamic);
                            if (!r.length && !n.length)
                                return;
                            clearTimeout(c.timer),
                            c.timer = setTimeout(function() {
                                r.length && r.forEach(function(r) {
                                    c.updateExposureNormal(r)
                                }),
                                n.length && n.forEach(function(r) {
                                    c.updateExposureDynamic(r)
                                })
                            }, 1e3)
                        } catch (r) {
                            (0,
                            x.asyncThrowError)(r)
                        }
                    }),
                    C(c, "updateExposureNormal", function(r) {
                        try {
                            var n, o, i = c.exposureCache.normal[r];
                            null != i && null !== (n = i.listening) && void 0 !== n && n.length && (i.listening = s(o = i.listening).call(o, function(r) {
                                if ((0,
                                _.isElementInViewport)(r, i.container)) {
                                    var n, o = c.xpath(r), u = o.index, a = o.xpath, s = o.dataInfo, l = o.scm, f = o.elemId, d = o.ext, p = (0,
                                    _.setEventSeq)(), h = {
                                        xpath: a,
                                        data_info: T(T({}, i.dataInfo), s),
                                        eventSeq: p,
                                        pgRefObj: {
                                            scm: void 0 === l ? {} : l,
                                            elemId: (void 0 === f ? "" : f) || v(n = "".concat(w.AUTOTRACK_KEY)).call(n, a),
                                            ext: void 0 === d ? {} : d
                                        }
                                    };
                                    return u > -1 && (h.index = u,
                                    h.pgRefObj.ext && (h.pgRefObj.ext.index = u)),
                                    c.tracke(h),
                                    !1
                                }
                                return !0
                            }),
                            i.listening.length || delete c.exposureCache.dynamic[r])
                        } catch (r) {
                            (0,
                            x.asyncThrowError)(r)
                        }
                    }),
                    C(c, "updateExposureDynamic", function(r) {
                        try {
                            var n = c.exposureCache.dynamic[r]
                              , o = function(o) {
                                var i;
                                null != o && null !== (i = o.listening) && void 0 !== i && i.length && (c.timerGroups[r] && clearTimeout(c.timerGroups[r]),
                                c.timerGroups[r] = setTimeout(function() {
                                    var i, u, a;
                                    o.listening = s(i = o.listening).call(i, function(r) {
                                        if ((0,
                                        _.isElementInViewport)(r, o.container)) {
                                            try {
                                                if (c.attr(r, "data-tlg-exposured-v3"))
                                                    return !1
                                            } catch (r) {
                                                (0,
                                                x.asyncThrowError)(r)
                                            }
                                            var n, i = c.xpath(r), u = i.index, a = i.xpath, s = i.dataInfo, l = i.scm, f = i.elemId, d = i.ext, p = {
                                                xpath: a,
                                                data_info: T(T({}, o.dataInfo), s),
                                                pgRefObj: {
                                                    scm: void 0 === l ? {} : l,
                                                    elemId: (void 0 === f ? "" : f) || v(n = "".concat(w.AUTOTRACK_KEY)).call(n, a),
                                                    ext: T(T({}, void 0 === d ? {} : d), {}, {
                                                        elmNode: r
                                                    })
                                                }
                                            };
                                            u > -1 && (p.index = u,
                                            p.pgRefObj.ext && (p.pgRefObj.ext.index = u),
                                            o.size && o.size > 0 && (p.index %= o.size,
                                            o.removed.push(1)));
                                            try {
                                                c.attr(r, "data-tlg-exposured-v3") || c.attr(r, "data-tlg-exposured-v3", !0)
                                            } catch (r) {
                                                (0,
                                                x.asyncThrowError)(r)
                                            }
                                            return c.tracke(p),
                                            !1
                                        }
                                        return !0
                                    }),
                                    n.size && n.removed.length === n.size && (delete c.exposureCache.dynamic[r],
                                    null === (u = n.observer) || void 0 === u || null === (a = u.disconnect) || void 0 === a || a.call(u)),
                                    c.timerGroups[r] = null
                                }, n.duration || 500))
                            };
                            Array.isArray(n) ? n.forEach(function(r) {
                                o(r)
                            }) : o(n)
                        } catch (r) {
                            (0,
                            x.asyncThrowError)(r)
                        }
                    }),
                    C(c, "tracke", function() {
                        var r = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : {};
                        try {
                            r.eventSeq = (0,
                            _.setEventSeq)();
                            var n, o, i, u = (null === (n = c.config) || void 0 === n || null === (n = n.collect) || void 0 === n || null === (n = n.exposure) || void 0 === n ? void 0 : n.maxSendCount) || 100, a = null === (o = c.config) || void 0 === o || null === (o = o.collect) || void 0 === o || null === (o = o.exposure) || void 0 === o ? void 0 : o.exposureInterval;
                            if (c.EHolder && clearTimeout(c.EHolder),
                            c.multipleExposure.push(r),
                            c.multipleExposure.length >= u)
                                return void c.sendData(h(i = c.multipleExposure).call(i, 0, u));
                            c.EHolder = setTimeout(function() {
                                c.sendData(c.multipleExposure),
                                c.multipleExposure = []
                            }, a || 1e3)
                        } catch (r) {
                            (0,
                            x.asyncThrowError)(r)
                        }
                    }),
                    C(c, "sendData", function(r) {
                        try {
                            var n = {
                                type: "e",
                                multiple_exposure: r
                            };
                            c.info("".concat(w.ReportEventType.exposure, " 事件上报数据: "), n),
                            c.report({
                                ev_type: w.ReportEventType.exposure,
                                payload: T({}, n)
                            })
                        } catch (r) {
                            (0,
                            x.asyncThrowError)(r)
                        }
                    }),
                    c.config = T({}, o),
                    c.type = "exposure",
                    c.client = r,
                    c.initDefaultConfig(),
                    c.init(),
                    c.info("exposure捕获 初始化"),
                    c
                }
                return function(r, n) {
                    if ("function" != typeof n && null !== n)
                        throw TypeError("Super expression must either be null or a function");
                    r.prototype = Object.create(n && n.prototype, {
                        constructor: {
                            value: r,
                            writable: !0,
                            configurable: !0
                        }
                    }),
                    Object.defineProperty(r, "prototype", {
                        writable: !1
                    }),
                    n && P(r, n)
                }(i, r),
                o = [{
                    key: "report",
                    value: function(r) {
                        this.client.report(r)
                    }
                }, {
                    key: "init",
                    value: function() {
                        this.info("开始监听 exposure 事件"),
                        this.exposure()
                    }
                }, {
                    key: "exposure",
                    value: function(r) {
                        var n = this;
                        try {
                            var o, i = (null == r ? void 0 : r.exposure) || r || (null === (o = this.config.collect) || void 0 === o || null === (o = o.exposure) || void 0 === o ? void 0 : o.config) || [];
                            i.push({
                                xpath: ".tlg-exposure-normal",
                                type: "normal"
                            }),
                            i.push({
                                type: "dynamic",
                                xpath: ".tlg-exposure-list",
                                container: {
                                    xpath: ".tlg-exposure-dynamic"
                                }
                            }),
                            Array.isArray(i) || (i = [i]),
                            i.forEach(function(r) {
                                if (r.type && "normal" !== r.type) {
                                    if ("dynamic" === r.type) {
                                        null !== (o = n.bindObserverTimer) && void 0 !== o && o[r.xpath] && clearTimeout(n.bindObserverTimer[r.xpath]);
                                        var o, i = T({
                                            attributes: !0,
                                            childList: !0,
                                            subtree: !0
                                        }, r.container), u = 0, a = r.maxCount || 30, c = 100;
                                        r.async && (c = 1e3);
                                        var s = function() {
                                            var o = n.xpath2selector(r.container.xpath)
                                              , l = document.querySelectorAll(o)
                                              , f = n.xpath2selector(r.xpath)
                                              , d = document.querySelectorAll(f);
                                            try {
                                                var p, b = null === (p = n.mutationObserverDynamic) || void 0 === p ? void 0 : m(p).call(p, function(n) {
                                                    var i;
                                                    return n.xpath === v(i = "".concat(o, "-")).call(i, r.xpath)
                                                });
                                                if (-1 !== b) {
                                                    var j, w, E = null === (j = n.mutationObserverDynamic) || void 0 === j ? void 0 : j[b];
                                                    null == E || E.disconnect(),
                                                    null === (w = n.mutationObserverDynamic) || void 0 === w || h(w).call(w, b, 1)
                                                }
                                            } catch (r) {
                                                (0,
                                                x.asyncThrowError)(r)
                                            }
                                            (!l.length || !d.length) && u++ < a || r.async && !l.length && !d.length ? n.bindObserverTimer[r.xpath] = setTimeout(s, c) : l.length && y(l).forEach(function(u, a) {
                                                var c, s, l, f = n.xpath2selector(r.xpath), d = u.querySelectorAll(f), p = v(c = "".concat(r.xpath, "-$")).call(c, a), h = new MutationObserver((0,
                                                _.mutationCallBack)(p, f, n.exposureCache, n.indexOf, n.updateExposureDynamic, n.mutationCallBackTimer)), m = n.query2JSON(n.attr(u, "data-tlg-config"));
                                                null == h || null === (l = h.observe) || void 0 === l || l.call(h, u, i),
                                                h.xpath = v(s = "".concat(o, "-")).call(s, r.xpath),
                                                n.mutationObserverDynamic.push(h);
                                                var b = {
                                                    listening: y(d),
                                                    size: r.size,
                                                    dataInfo: r.dataInfo,
                                                    removed: [],
                                                    duration: r.duration,
                                                    observer: h,
                                                    container: u
                                                };
                                                (b = g(b, m)).size = b.size ? Number(b.size) : 0,
                                                n.exposureCache.dynamic[p] = b,
                                                n.updateExposureAdapter()
                                            })
                                        };
                                        s()
                                    } else
                                        "repeated" === r.type && n.repeatedExposure(r)
                                } else {
                                    var l = n.xpath2selector(r.xpath)
                                      , f = document.querySelectorAll(l);
                                    f.length && (n.exposureCache.normal[r.xpath] = {
                                        listening: y(f),
                                        dataInfo: r.dataInfo,
                                        container: r.container
                                    })
                                }
                            }),
                            (0,
                            _.removeEventListener)(window, "resize", this.updateExposureAdapter),
                            (0,
                            _.removeEventListener)(window, "scroll", this.updateExposureAdapter),
                            (0,
                            _.addEventListener)(window, "resize", this.updateExposureAdapter),
                            (0,
                            _.addEventListener)(window, "scroll", this.updateExposureAdapter),
                            this.updateExposureAdapter()
                        } catch (r) {
                            (0,
                            x.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "info",
                    value: function() {
                        for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                            i[u] = arguments[u];
                        return (n = this.client.logs).info.apply(n, v(r = ["Exposure"]).call(r, i))
                    }
                }, {
                    key: "error",
                    value: function() {
                        for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                            i[u] = arguments[u];
                        return (n = this.client.logs).error.apply(n, v(r = ["Exposure"]).call(r, i))
                    }
                }, {
                    key: "destroy",
                    value: function() {
                        try {
                            var r, n;
                            null !== (r = this.mutationObserverDynamic) && void 0 !== r && r.length && this.mutationObserverDynamic.forEach(function(r) {
                                var n;
                                null == r || null === (n = r.disconnect) || void 0 === n || n.call(r)
                            }),
                            null !== (n = this.intersectionObserver) && void 0 !== n && n.length && this.intersectionObserver.forEach(function(r) {
                                var n;
                                null == r || null === (n = r.disconnect) || void 0 === n || n.call(r)
                            }),
                            (0,
                            _.removeEventListener)(window, "resize", this.updateExposureAdapter),
                            (0,
                            _.removeEventListener)(window, "scroll", this.updateExposureAdapter),
                            this.initDefaultConfig(),
                            this.mutationObserverDynamic = [],
                            this.info("exposure 事件 destroy")
                        } catch (r) {
                            (0,
                            x.asyncThrowError)(r)
                        }
                    }
                }],
                function(r, n) {
                    for (var o = 0; o < n.length; o++) {
                        var i = n[o];
                        i.enumerable = i.enumerable || !1,
                        i.configurable = !0,
                        "value"in i && (i.writable = !0),
                        Object.defineProperty(r, A(i.key), i)
                    }
                }(i.prototype, o),
                Object.defineProperty(i, "prototype", {
                    writable: !1
                }),
                i
            }(j.default)
        }
    })
      , n6 = u({
        "src/collect/pageView/index.ts": function(r) {
            var o, i, u, a = tw(), c = tO(), s = tX(), l = tS(), f = tC(), d = tM(), p = tB(), v = tH(), h = tG(), y = tZ();
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.PageView = void 0,
            r.default = function(r) {
                for (var n, o, i = arguments.length, u = Array(i > 1 ? i - 1 : 0), a = 1; a < i; a++)
                    u[a - 1] = arguments[a];
                var c, l = E({}, u)[0];
                return null === (n = null == l || null === (o = l.collect) || void 0 === o || null === (o = o.pageView) || void 0 === o ? void 0 : o.enable) || void 0 === n || n ? function(r, n, o) {
                    if (x())
                        return s.apply(null, arguments);
                    var i = [null];
                    i.push.apply(i, n);
                    var u = new (r.bind.apply(r, i));
                    return o && w(u, o.prototype),
                    u
                }(S, y(c = [r]).call(c, u)) : null
            }
            ;
            var m = nI()
              , g = nK()
              , b = nd();
            function j(r) {
                return (j = "function" == typeof a && "symbol" == typeof c ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof a && r.constructor === a && r !== a.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            function w(r, n) {
                return (w = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(r, n) {
                    return r.__proto__ = n,
                    r
                }
                )(r, n)
            }
            function x() {
                try {
                    var r = !Boolean.prototype.valueOf.call(s(Boolean, [], function() {}))
                } catch (r) {}
                return (x = function() {
                    return !!r
                }
                )()
            }
            function _(r, n) {
                var o = l(r);
                if (f) {
                    var i = f(r);
                    n && (i = d(i).call(i, function(n) {
                        return p(r, n).enumerable
                    })),
                    o.push.apply(o, i)
                }
                return o
            }
            function E(r) {
                for (var n = 1; n < arguments.length; n++) {
                    var o = null != arguments[n] ? arguments[n] : {};
                    n % 2 ? _(Object(o), !0).forEach(function(n) {
                        T(r, n, o[n])
                    }) : v ? Object.defineProperties(r, v(o)) : _(Object(o)).forEach(function(n) {
                        Object.defineProperty(r, n, p(o, n))
                    })
                }
                return r
            }
            function O(r, n) {
                for (var o = 0; o < n.length; o++) {
                    var i = n[o];
                    i.enumerable = i.enumerable || !1,
                    i.configurable = !0,
                    "value"in i && (i.writable = !0),
                    Object.defineProperty(r, k(i.key), i)
                }
            }
            function T(r, n, o) {
                return (n = k(n))in r ? Object.defineProperty(r, n, {
                    value: o,
                    enumerable: !0,
                    configurable: !0,
                    writable: !0
                }) : r[n] = o,
                r
            }
            function k(r) {
                var n = function(r, n) {
                    if ("object" != j(r) || !r)
                        return r;
                    var o = r[h];
                    if (void 0 !== o) {
                        var i = o.call(r, n || "default");
                        if ("object" != j(i))
                            return i;
                        throw TypeError("@@toPrimitive must return a primitive value.")
                    }
                    return ("string" === n ? String : Number)(r)
                }(r, "string");
                return "symbol" == j(n) ? n : n + ""
            }
            var S = (o = function r(o, i) {
                var u = this;
                (function(r, o) {
                    if (!n(r, o))
                        throw TypeError("Cannot call a class as a function")
                }
                )(this, r),
                T(this, "config", {}),
                T(this, "trackp", function(r) {
                    try {
                        var n = (0,
                        b.setEventSeq)()
                          , o = {
                            type: m.ReportEventType.pageView,
                            data_info: r || {},
                            eventSeq: n,
                            pgRefObj: {
                                scm: u.config.scm,
                                ext: u.config.ext
                            }
                        };
                        u.info("".concat(m.ReportEventType.pageView, " 事件上报数据: "), o),
                        u.report({
                            ev_type: m.ReportEventType.pageView,
                            payload: E({}, o)
                        })
                    } catch (r) {
                        (0,
                        g.asyncThrowError)(r)
                    }
                }),
                this.config = E({}, i),
                this.type = "pageView",
                this.client = o,
                this.info("pageView捕获 初始化"),
                this.init()
            }
            ,
            i = [{
                key: "report",
                value: function(r) {
                    this.client.initTrackP = !0,
                    this.client.report(r)
                }
            }, {
                key: "init",
                value: function() {
                    var r;
                    this.info("开始发送p码事件"),
                    null !== (r = this.client) && void 0 !== r && r.bridgeTrackP ? this.info("已通过桥接事件发送p码事件") : this.trackp()
                }
            }, {
                key: "destroy",
                value: function() {}
            }, {
                key: "info",
                value: function() {
                    for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                        i[u] = arguments[u];
                    return (n = this.client.logs).info.apply(n, y(r = ["pageView"]).call(r, i))
                }
            }, {
                key: "error",
                value: function() {
                    for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                        i[u] = arguments[u];
                    return (n = this.client.logs).error.apply(n, y(r = ["pageView"]).call(r, i))
                }
            }],
            O(o.prototype, i),
            u && O(o, u),
            Object.defineProperty(o, "prototype", {
                writable: !1
            }),
            r.PageView = o)
        }
    })
      , n4 = u({
        "src/collect/showDialog/index.ts": function(r) {
            var o = tw()
              , i = tO()
              , u = tX()
              , a = tS()
              , c = tC()
              , s = tM()
              , l = tB()
              , f = tH()
              , d = t2()
              , p = tG()
              , v = r8()
              , h = tZ();
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.ShowDialog = void 0,
            r.default = function(r) {
                for (var n, o, i = arguments.length, a = Array(i > 1 ? i - 1 : 0), c = 1; c < i; c++)
                    a[c - 1] = arguments[c];
                var s, l = _({}, a)[0];
                return null === (n = null == l || null === (o = l.collect) || void 0 === o || null === (o = o.showDialog) || void 0 === o ? void 0 : o.enable) || void 0 === n || n ? function(r, n, o) {
                    if (E())
                        return u.apply(null, arguments);
                    var i = [null];
                    i.push.apply(i, n);
                    var a = new (r.bind.apply(r, i));
                    return o && T(a, o.prototype),
                    a
                }(P, h(s = [r]).call(s, a)) : null
            }
            ;
            var y, m = (y = nR()) && y.__esModule ? y : {
                default: y
            }, g = nI(), b = nK(), j = nd();
            function w(r) {
                return (w = "function" == typeof o && "symbol" == typeof i ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof o && r.constructor === o && r !== o.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            function x(r, n) {
                var o = a(r);
                if (c) {
                    var i = c(r);
                    n && (i = s(i).call(i, function(n) {
                        return l(r, n).enumerable
                    })),
                    o.push.apply(o, i)
                }
                return o
            }
            function _(r) {
                for (var n = 1; n < arguments.length; n++) {
                    var o = null != arguments[n] ? arguments[n] : {};
                    n % 2 ? x(Object(o), !0).forEach(function(n) {
                        k(r, n, o[n])
                    }) : f ? Object.defineProperties(r, f(o)) : x(Object(o)).forEach(function(n) {
                        Object.defineProperty(r, n, l(o, n))
                    })
                }
                return r
            }
            function E() {
                try {
                    var r = !Boolean.prototype.valueOf.call(u(Boolean, [], function() {}))
                } catch (r) {}
                return (E = function() {
                    return !!r
                }
                )()
            }
            function O(r) {
                return (O = Object.setPrototypeOf ? d.bind() : function(r) {
                    return r.__proto__ || d(r)
                }
                )(r)
            }
            function T(r, n) {
                return (T = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(r, n) {
                    return r.__proto__ = n,
                    r
                }
                )(r, n)
            }
            function k(r, n, o) {
                return (n = S(n))in r ? Object.defineProperty(r, n, {
                    value: o,
                    enumerable: !0,
                    configurable: !0,
                    writable: !0
                }) : r[n] = o,
                r
            }
            function S(r) {
                var n = function(r, n) {
                    if ("object" != w(r) || !r)
                        return r;
                    var o = r[p];
                    if (void 0 !== o) {
                        var i = o.call(r, n || "default");
                        if ("object" != w(i))
                            return i;
                        throw TypeError("@@toPrimitive must return a primitive value.")
                    }
                    return ("string" === n ? String : Number)(r)
                }(r, "string");
                return "symbol" == w(n) ? n : n + ""
            }
            var P = r.ShowDialog = function(r) {
                var o;
                function i(r, o) {
                    var a, c, s;
                    return function(r, o) {
                        if (!n(r, o))
                            throw TypeError("Cannot call a class as a function")
                    }(this, i),
                    k((c = i,
                    s = [{
                        dialogAlias: o.dialogAlias
                    }],
                    c = O(c),
                    a = function(r, n) {
                        if (n && ("object" == w(n) || "function" == typeof n))
                            return n;
                        if (void 0 !== n)
                            throw TypeError("Derived constructors may only return object or undefined");
                        return function(r) {
                            if (void 0 === r)
                                throw ReferenceError("this hasn't been initialised - super() hasn't been called");
                            return r
                        }(r)
                    }(this, E() ? u(c, s || [], O(this).constructor) : c.apply(this, s))), "config", {}),
                    k(a, "mutationObserver", null),
                    k(a, "mutationObserverLayer", function() {
                        try {
                            var r, n;
                            MutationObserver && (a.mutationObserver = new MutationObserver((function(r) {
                                null == r || r.forEach(function(r) {
                                    if ("childList" === r.type && r.addedNodes) {
                                        var n, o = r.addedNodes;
                                        null === (n = v(o)) || void 0 === n || n.forEach(function(r) {
                                            r.nodeType && 1 === r.nodeType && a.isDialog(r) && a.tracks(r)
                                        })
                                    }
                                })
                            }
                            ).bind(a)),
                            null === (r = a.mutationObserver) || void 0 === r || null === (n = r.observe) || void 0 === n || n.call(r, document.body, {
                                attributes: !1,
                                childList: !0,
                                subtree: !1
                            }))
                        } catch (r) {
                            (0,
                            b.asyncThrowError)(r)
                        }
                    }),
                    a.config = _({}, o),
                    a.type = "showDialog",
                    a.mutationObserver = null,
                    a.client = r,
                    a.init(),
                    a.info("ShowDialog事件 初始化"),
                    a
                }
                return function(r, n) {
                    if ("function" != typeof n && null !== n)
                        throw TypeError("Super expression must either be null or a function");
                    r.prototype = Object.create(n && n.prototype, {
                        constructor: {
                            value: r,
                            writable: !0,
                            configurable: !0
                        }
                    }),
                    Object.defineProperty(r, "prototype", {
                        writable: !1
                    }),
                    n && T(r, n)
                }(i, r),
                o = [{
                    key: "report",
                    value: function(r) {
                        this.client.report(r)
                    }
                }, {
                    key: "init",
                    value: function() {
                        this.mutationObserverLayer(),
                        this.info("开始监听 ShowDialog 事件")
                    }
                }, {
                    key: "tracks",
                    value: function(r) {
                        try {
                            var n = (0,
                            j.setEventSeq)()
                              , o = this.xpath(r).dataInfo
                              , i = this.getDialogScmAndElemId(r)
                              , u = i.scm
                              , a = i.elemId
                              , c = i.ext
                              , s = {
                                type: g.ReportEventType.showDialog,
                                data_info: o,
                                eventSeq: n,
                                pgRefObj: {
                                    scm: void 0 === u ? {} : u,
                                    elemId: void 0 === a ? "" : a,
                                    ext: void 0 === c ? {} : c
                                }
                            };
                            this.info("".concat(g.ReportEventType.showDialog, " 事件上报数据: "), s),
                            this.report({
                                ev_type: g.ReportEventType.showDialog,
                                payload: _({}, s)
                            })
                        } catch (r) {
                            (0,
                            b.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "info",
                    value: function() {
                        for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                            i[u] = arguments[u];
                        return (n = this.client.logs).info.apply(n, h(r = ["ShowDialog"]).call(r, i))
                    }
                }, {
                    key: "error",
                    value: function() {
                        for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                            i[u] = arguments[u];
                        return (n = this.client.logs).error.apply(n, h(r = ["ShowDialog"]).call(r, i))
                    }
                }, {
                    key: "destroy",
                    value: function() {
                        try {
                            var r, n;
                            null === (r = this.mutationObserver) || void 0 === r || null === (n = r.disconnect) || void 0 === n || n.call(r),
                            this.mutationObserver = null,
                            this.info("showDailog 事件 destroy")
                        } catch (r) {
                            (0,
                            b.asyncThrowError)(r)
                        }
                    }
                }],
                function(r, n) {
                    for (var o = 0; o < n.length; o++) {
                        var i = n[o];
                        i.enumerable = i.enumerable || !1,
                        i.configurable = !0,
                        "value"in i && (i.writable = !0),
                        Object.defineProperty(r, S(i.key), i)
                    }
                }(i.prototype, o),
                Object.defineProperty(i, "prototype", {
                    writable: !1
                }),
                i
            }(m.default)
        }
    })
      , n8 = u({
        "src/collect/collects.ts": function(r) {
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            Object.defineProperty(r, "aliveCreater", {
                enumerable: !0,
                get: function() {
                    return o.default
                }
            }),
            Object.defineProperty(r, "clickCreater", {
                enumerable: !0,
                get: function() {
                    return n.default
                }
            }),
            Object.defineProperty(r, "exposureCreater", {
                enumerable: !0,
                get: function() {
                    return i.default
                }
            }),
            Object.defineProperty(r, "pageViewCreater", {
                enumerable: !0,
                get: function() {
                    return u.default
                }
            }),
            Object.defineProperty(r, "showDialogCreater", {
                enumerable: !0,
                get: function() {
                    return a.default
                }
            });
            var n = c(nW())
              , o = c(nY())
              , i = c(n3())
              , u = c(n6())
              , a = c(n4());
            function c(r) {
                return r && r.__esModule ? r : {
                    default: r
                }
            }
        }
    })
      , n7 = u({
        "src/collect/index.ts": function(r) {
            var n = tw()
              , o = tO()
              , i = nE()
              , u = tB()
              , a = tS();
            function c(r) {
                return (c = "function" == typeof n && "symbol" == typeof o ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof n && r.constructor === n && r !== n.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.addCollect = p,
            r.getCollects = void 0;
            var s = function(r, n) {
                if (r && r.__esModule)
                    return r;
                if (null === r || "object" != c(r) && "function" != typeof r)
                    return {
                        default: r
                    };
                var o = f(void 0);
                if (o && o.has(r))
                    return o.get(r);
                var i = {
                    __proto__: null
                }
                  , a = Object.defineProperty && u;
                for (var s in r)
                    if ("default" !== s && ({}).hasOwnProperty.call(r, s)) {
                        var l = a ? u(r, s) : null;
                        l && (l.get || l.set) ? Object.defineProperty(i, s, l) : i[s] = r[s]
                    }
                return i.default = r,
                o && o.set(r, i),
                i
            }(n8())
              , l = nK();
            function f(r) {
                if ("function" != typeof i)
                    return null;
                var n = new i
                  , o = new i;
                return (f = function(r) {
                    return r ? o : n
                }
                )(r)
            }
            var d = [];
            function p(r) {
                try {
                    if (!r || !d || -1 !== (null == d ? void 0 : d.indexOf(r)))
                        return;
                    d.push(r)
                } catch (r) {
                    (0,
                    l.asyncThrowError)(r)
                }
            }
            (function() {
                if (s)
                    try {
                        a(s).forEach(function(r) {
                            r && p(s[r])
                        })
                    } catch (r) {
                        (0,
                        l.asyncThrowError)(r)
                    }
            }
            )(),
            r.getCollects = function() {
                return d
            }
        }
    })
      , n9 = u({
        "src/configManager/index.ts": function(r) {
            var o = tw()
              , i = tO()
              , u = t2()
              , a = rG()
              , c = r2()
              , s = tS()
              , l = tC()
              , f = tM()
              , d = tB()
              , p = tH()
              , v = tX()
              , h = tG()
              , y = tZ();
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.ConfigManager = void 0,
            r.default = function() {
                return {}
            }
            ;
            var m = x(np())
              , g = nK()
              , b = nI()
              , j = nd()
              , w = x(no());
            function x(r) {
                return r && r.__esModule ? r : {
                    default: r
                }
            }
            function _(r) {
                return (_ = "function" == typeof o && "symbol" == typeof i ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof o && r.constructor === o && r !== o.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            function E() {
                E = function() {
                    return i
                }
                ;
                var r, i = {}, s = Object.prototype, l = s.hasOwnProperty, f = Object.defineProperty || function(r, n, o) {
                    r[n] = o.value
                }
                , d = "function" == typeof o ? o : {}, p = d.iterator || "@@iterator", v = d.asyncIterator || "@@asyncIterator", h = d.toStringTag || "@@toStringTag";
                function y(r, n, o) {
                    return Object.defineProperty(r, n, {
                        value: o,
                        enumerable: !0,
                        configurable: !0,
                        writable: !0
                    }),
                    r[n]
                }
                try {
                    y({}, "")
                } catch (r) {
                    y = function(r, n, o) {
                        return r[n] = o
                    }
                }
                function m(o, i, u, a) {
                    var c, s, l, d, p = Object.create((i && n(i.prototype, O) ? i : O).prototype);
                    return f(p, "_invoke", {
                        value: (c = o,
                        s = u,
                        l = new M(a || []),
                        d = b,
                        function(n, o) {
                            if (d === j)
                                throw Error("Generator is already running");
                            if (d === w) {
                                if ("throw" === n)
                                    throw o;
                                return {
                                    value: r,
                                    done: !0
                                }
                            }
                            for (l.method = n,
                            l.arg = o; ; ) {
                                var i = l.delegate;
                                if (i) {
                                    var u = function n(o, i) {
                                        var u = i.method
                                          , a = o.iterator[u];
                                        if (a === r)
                                            return i.delegate = null,
                                            "throw" === u && o.iterator.return && (i.method = "return",
                                            i.arg = r,
                                            n(o, i),
                                            "throw" === i.method) || "return" !== u && (i.method = "throw",
                                            i.arg = TypeError("The iterator does not provide a '" + u + "' method")),
                                            x;
                                        var c = g(a, o.iterator, i.arg);
                                        if ("throw" === c.type)
                                            return i.method = "throw",
                                            i.arg = c.arg,
                                            i.delegate = null,
                                            x;
                                        var s = c.arg;
                                        return s ? s.done ? (i[o.resultName] = s.value,
                                        i.next = o.nextLoc,
                                        "return" !== i.method && (i.method = "next",
                                        i.arg = r),
                                        i.delegate = null,
                                        x) : s : (i.method = "throw",
                                        i.arg = TypeError("iterator result is not an object"),
                                        i.delegate = null,
                                        x)
                                    }(i, l);
                                    if (u) {
                                        if (u === x)
                                            continue;
                                        return u
                                    }
                                }
                                if ("next" === l.method)
                                    l.sent = l._sent = l.arg;
                                else if ("throw" === l.method) {
                                    if (d === b)
                                        throw d = w,
                                        l.arg;
                                    l.dispatchException(l.arg)
                                } else
                                    "return" === l.method && l.abrupt("return", l.arg);
                                d = j;
                                var a = g(c, s, l);
                                if ("normal" === a.type) {
                                    if (d = l.done ? w : "suspendedYield",
                                    a.arg === x)
                                        continue;
                                    return {
                                        value: a.arg,
                                        done: l.done
                                    }
                                }
                                "throw" === a.type && (d = w,
                                l.method = "throw",
                                l.arg = a.arg)
                            }
                        }
                        )
                    }),
                    p
                }
                function g(r, n, o) {
                    try {
                        return {
                            type: "normal",
                            arg: r.call(n, o)
                        }
                    } catch (r) {
                        return {
                            type: "throw",
                            arg: r
                        }
                    }
                }
                i.wrap = m;
                var b = "suspendedStart"
                  , j = "executing"
                  , w = "completed"
                  , x = {};
                function O() {}
                function T() {}
                function k() {}
                var S = {};
                y(S, p, function() {
                    return this
                });
                var P = u && u(u(N([])));
                P && P !== s && l.call(P, p) && (S = P);
                var C = k.prototype = O.prototype = Object.create(S);
                function A(r) {
                    ["next", "throw", "return"].forEach(function(n) {
                        y(r, n, function(r) {
                            return this._invoke(n, r)
                        })
                    })
                }
                function I(r, n) {
                    var o;
                    f(this, "_invoke", {
                        value: function(i, u) {
                            function a() {
                                return new n(function(o, a) {
                                    (function o(i, u, a, c) {
                                        var s = g(r[i], r, u);
                                        if ("throw" !== s.type) {
                                            var f = s.arg
                                              , d = f.value;
                                            return d && "object" == _(d) && l.call(d, "__await") ? n.resolve(d.__await).then(function(r) {
                                                o("next", r, a, c)
                                            }, function(r) {
                                                o("throw", r, a, c)
                                            }) : n.resolve(d).then(function(r) {
                                                f.value = r,
                                                a(f)
                                            }, function(r) {
                                                return o("throw", r, a, c)
                                            })
                                        }
                                        c(s.arg)
                                    }
                                    )(i, u, o, a)
                                }
                                )
                            }
                            return o = o ? o.then(a, a) : a()
                        }
                    })
                }
                function R(r) {
                    var n = {
                        tryLoc: r[0]
                    };
                    1 in r && (n.catchLoc = r[1]),
                    2 in r && (n.finallyLoc = r[2],
                    n.afterLoc = r[3]),
                    this.tryEntries.push(n)
                }
                function L(r) {
                    var n = r.completion || {};
                    n.type = "normal",
                    delete n.arg,
                    r.completion = n
                }
                function M(r) {
                    this.tryEntries = [{
                        tryLoc: "root"
                    }],
                    r.forEach(R, this),
                    this.reset(!0)
                }
                function N(n) {
                    if (n || "" === n) {
                        var o = n[p];
                        if (o)
                            return o.call(n);
                        if ("function" == typeof n.next)
                            return n;
                        if (!isNaN(n.length)) {
                            var i = -1
                              , u = function o() {
                                for (; ++i < n.length; )
                                    if (l.call(n, i))
                                        return o.value = n[i],
                                        o.done = !1,
                                        o;
                                return o.value = r,
                                o.done = !0,
                                o
                            };
                            return u.next = u
                        }
                    }
                    throw TypeError(_(n) + " is not iterable")
                }
                return T.prototype = k,
                f(C, "constructor", {
                    value: k,
                    configurable: !0
                }),
                f(k, "constructor", {
                    value: T,
                    configurable: !0
                }),
                T.displayName = y(k, h, "GeneratorFunction"),
                i.isGeneratorFunction = function(r) {
                    var n = "function" == typeof r && r.constructor;
                    return !!n && (n === T || "GeneratorFunction" === (n.displayName || n.name))
                }
                ,
                i.mark = function(r) {
                    return Object.setPrototypeOf ? Object.setPrototypeOf(r, k) : (r.__proto__ = k,
                    y(r, h, "GeneratorFunction")),
                    r.prototype = Object.create(C),
                    r
                }
                ,
                i.awrap = function(r) {
                    return {
                        __await: r
                    }
                }
                ,
                A(I.prototype),
                y(I.prototype, v, function() {
                    return this
                }),
                i.AsyncIterator = I,
                i.async = function(r, n, o, u, c) {
                    void 0 === c && (c = a);
                    var s = new I(m(r, n, o, u),c);
                    return i.isGeneratorFunction(n) ? s : s.next().then(function(r) {
                        return r.done ? r.value : s.next()
                    })
                }
                ,
                A(C),
                y(C, h, "Generator"),
                y(C, p, function() {
                    return this
                }),
                y(C, "toString", function() {
                    return "[object Generator]"
                }),
                i.keys = function(r) {
                    var n = Object(r)
                      , o = [];
                    for (var i in n)
                        o.push(i);
                    return o.reverse(),
                    function r() {
                        for (; o.length; ) {
                            var i = o.pop();
                            if (i in n)
                                return r.value = i,
                                r.done = !1,
                                r
                        }
                        return r.done = !0,
                        r
                    }
                }
                ,
                i.values = N,
                M.prototype = {
                    constructor: M,
                    reset: function(n) {
                        if (this.prev = 0,
                        this.next = 0,
                        this.sent = this._sent = r,
                        this.done = !1,
                        this.delegate = null,
                        this.method = "next",
                        this.arg = r,
                        this.tryEntries.forEach(L),
                        !n)
                            for (var o in this)
                                "t" === o.charAt(0) && l.call(this, o) && !isNaN(+c(o).call(o, 1)) && (this[o] = r)
                    },
                    stop: function() {
                        this.done = !0;
                        var r = this.tryEntries[0].completion;
                        if ("throw" === r.type)
                            throw r.arg;
                        return this.rval
                    },
                    dispatchException: function(n) {
                        if (this.done)
                            throw n;
                        var o = this;
                        function i(i, u) {
                            return c.type = "throw",
                            c.arg = n,
                            o.next = i,
                            u && (o.method = "next",
                            o.arg = r),
                            !!u
                        }
                        for (var u = this.tryEntries.length - 1; u >= 0; --u) {
                            var a = this.tryEntries[u]
                              , c = a.completion;
                            if ("root" === a.tryLoc)
                                return i("end");
                            if (a.tryLoc <= this.prev) {
                                var s = l.call(a, "catchLoc")
                                  , f = l.call(a, "finallyLoc");
                                if (s && f) {
                                    if (this.prev < a.catchLoc)
                                        return i(a.catchLoc, !0);
                                    if (this.prev < a.finallyLoc)
                                        return i(a.finallyLoc)
                                } else if (s) {
                                    if (this.prev < a.catchLoc)
                                        return i(a.catchLoc, !0)
                                } else {
                                    if (!f)
                                        throw Error("try statement without catch or finally");
                                    if (this.prev < a.finallyLoc)
                                        return i(a.finallyLoc)
                                }
                            }
                        }
                    },
                    abrupt: function(r, n) {
                        for (var o = this.tryEntries.length - 1; o >= 0; --o) {
                            var i = this.tryEntries[o];
                            if (i.tryLoc <= this.prev && l.call(i, "finallyLoc") && this.prev < i.finallyLoc) {
                                var u = i;
                                break
                            }
                        }
                        u && ("break" === r || "continue" === r) && u.tryLoc <= n && n <= u.finallyLoc && (u = null);
                        var a = u ? u.completion : {};
                        return a.type = r,
                        a.arg = n,
                        u ? (this.method = "next",
                        this.next = u.finallyLoc,
                        x) : this.complete(a)
                    },
                    complete: function(r, n) {
                        if ("throw" === r.type)
                            throw r.arg;
                        return "break" === r.type || "continue" === r.type ? this.next = r.arg : "return" === r.type ? (this.rval = this.arg = r.arg,
                        this.method = "return",
                        this.next = "end") : "normal" === r.type && n && (this.next = n),
                        x
                    },
                    finish: function(r) {
                        for (var n = this.tryEntries.length - 1; n >= 0; --n) {
                            var o = this.tryEntries[n];
                            if (o.finallyLoc === r)
                                return this.complete(o.completion, o.afterLoc),
                                L(o),
                                x
                        }
                    },
                    catch: function(r) {
                        for (var n = this.tryEntries.length - 1; n >= 0; --n) {
                            var o = this.tryEntries[n];
                            if (o.tryLoc === r) {
                                var i = o.completion;
                                if ("throw" === i.type) {
                                    var u = i.arg;
                                    L(o)
                                }
                                return u
                            }
                        }
                        throw Error("illegal catch attempt")
                    },
                    delegateYield: function(n, o, i) {
                        return this.delegate = {
                            iterator: N(n),
                            resultName: o,
                            nextLoc: i
                        },
                        "next" === this.method && (this.arg = r),
                        x
                    }
                },
                i
            }
            function O(r, n, o, i, u, c, s) {
                try {
                    var l = r[c](s)
                      , f = l.value
                } catch (r) {
                    return void o(r)
                }
                l.done ? n(f) : a.resolve(f).then(i, u)
            }
            function T(r, n) {
                var o = s(r);
                if (l) {
                    var i = l(r);
                    n && (i = f(i).call(i, function(n) {
                        return d(r, n).enumerable
                    })),
                    o.push.apply(o, i)
                }
                return o
            }
            function k(r) {
                for (var n = 1; n < arguments.length; n++) {
                    var o = null != arguments[n] ? arguments[n] : {};
                    n % 2 ? T(Object(o), !0).forEach(function(n) {
                        I(r, n, o[n])
                    }) : p ? Object.defineProperties(r, p(o)) : T(Object(o)).forEach(function(n) {
                        Object.defineProperty(r, n, d(o, n))
                    })
                }
                return r
            }
            function S(r, n) {
                for (var o = 0; o < n.length; o++) {
                    var i = n[o];
                    i.enumerable = i.enumerable || !1,
                    i.configurable = !0,
                    "value"in i && (i.writable = !0),
                    Object.defineProperty(r, R(i.key), i)
                }
            }
            function P() {
                try {
                    var r = !Boolean.prototype.valueOf.call(v(Boolean, [], function() {}))
                } catch (r) {}
                return (P = function() {
                    return !!r
                }
                )()
            }
            function C(r) {
                return (C = Object.setPrototypeOf ? u.bind() : function(r) {
                    return r.__proto__ || u(r)
                }
                )(r)
            }
            function A(r, n) {
                return (A = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(r, n) {
                    return r.__proto__ = n,
                    r
                }
                )(r, n)
            }
            function I(r, n, o) {
                return (n = R(n))in r ? Object.defineProperty(r, n, {
                    value: o,
                    enumerable: !0,
                    configurable: !0,
                    writable: !0
                }) : r[n] = o,
                r
            }
            function R(r) {
                var n = function(r, n) {
                    if ("object" != _(r) || !r)
                        return r;
                    var o = r[h];
                    if (void 0 !== o) {
                        var i = o.call(r, n || "default");
                        if ("object" != _(i))
                            return i;
                        throw TypeError("@@toPrimitive must return a primitive value.")
                    }
                    return ("string" === n ? String : Number)(r)
                }(r, "string");
                return "symbol" == _(n) ? n : n + ""
            }
            var L = function() {};
            r.ConfigManager = function(r) {
                var o, i, u, c;
                function s(r, o, i) {
                    var u, a, c;
                    return function(r, o) {
                        if (!n(r, o))
                            throw TypeError("Cannot call a class as a function")
                    }(this, s),
                    I((a = C(a = s),
                    u = function(r, n) {
                        if (n && ("object" == _(n) || "function" == typeof n))
                            return n;
                        if (void 0 !== n)
                            throw TypeError("Derived constructors may only return object or undefined");
                        return function(r) {
                            if (void 0 === r)
                                throw ReferenceError("this hasn't been initialised - super() hasn't been called");
                            return r
                        }(r)
                    }(this, P() ? v(a, [], C(this).constructor) : a.apply(this, c))), "onReadyCallback", L),
                    u.config = k(k({}, m.default), o),
                    u.client = r,
                    u.userConfig = i || {},
                    u.useAppUuid(),
                    u
                }
                return function(r, n) {
                    if ("function" != typeof n && null !== n)
                        throw TypeError("Super expression must either be null or a function");
                    r.prototype = Object.create(n && n.prototype, {
                        constructor: {
                            value: r,
                            writable: !0,
                            configurable: !0
                        }
                    }),
                    Object.defineProperty(r, "prototype", {
                        writable: !1
                    }),
                    n && A(r, n)
                }(s, r),
                o = [{
                    key: "onReady",
                    value: (u = E().mark(function r(n) {
                        return E().wrap(function(r) {
                            for (; ; )
                                switch (r.prev = r.next) {
                                case 0:
                                    if (this.onReadyCallback = n,
                                    "function" == typeof n) {
                                        r.next = 4;
                                        break
                                    }
                                    return this.error("获取配置回调不是function"),
                                    r.abrupt("return");
                                case 4:
                                    try {
                                        this.build(this.config),
                                        this.info("configManager onReady"),
                                        this.emit(b.LifecycleEvent.config, this.config, this),
                                        this.onReadyCallback(this.config)
                                    } catch (r) {
                                        this.error("获取配置失败", r),
                                        this.client.destroy(),
                                        (0,
                                        j.asyncThrowError)(r)
                                    }
                                case 5:
                                case "end":
                                    return r.stop()
                                }
                        }, r, this)
                    }),
                    c = function() {
                        var r = this
                          , n = arguments;
                        return new a(function(o, i) {
                            var a = u.apply(r, n);
                            function c(r) {
                                O(a, o, i, c, s, "next", r)
                            }
                            function s(r) {
                                O(a, o, i, c, s, "throw", r)
                            }
                            c(void 0)
                        }
                        )
                    }
                    ,
                    function(r) {
                        return c.apply(this, arguments)
                    }
                    )
                }, {
                    key: "build",
                    value: function(r) {
                        try {
                            null !== (n = this.userConfig) && void 0 !== n && null !== (n = n.collect) && void 0 !== n && null !== (n = n.exposure) && void 0 !== n && n.config && (this.userConfig.collect.exposure.config = null === (i = this.userConfig) || void 0 === i || null === (i = i.collect) || void 0 === i ? void 0 : y(o = i.exposure.config).call(o, this.userConfig.exposure));
                            var n, o, i, u = this.getDefauleConfig(), a = u.trackCache, c = u.sessionId;
                            (0,
                            j.generateSessionId)(),
                            this.userConfig = k(k(k(k({}, this.userConfig), a), (0,
                            j.generateSequence)()), {}, {
                                sessionId: c
                            });
                            var s = this.deepMerge(r, this.userConfig);
                            this.setConfig(s)
                        } catch (r) {
                            (0,
                            j.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "getDefauleConfig",
                    value: function() {
                        try {
                            var r, n, o, i = encodeURIComponent(document.referrer);
                            null !== (n = window) && void 0 !== n && null !== (n = n.tlogCacheRefer) && void 0 !== n && n.length ? i = window.tlogCacheRefer[window.tlogCacheRefer.length - 1] : window.tlogCacheRefer = [];
                            var u = location.href
                              , a = (0,
                            j.generateUuid)()
                              , c = encodeURIComponent(u);
                            return null === (o = window.tlogCacheRefer) || void 0 === o || o.push(encodeURIComponent(u)),
                            {
                                trackCache: {
                                    url: c,
                                    refer: i,
                                    resolution: window.screen ? y(r = "".concat(window.screen.width, "X")).call(r, window.screen.height) : "0X0",
                                    page_md5: (0,
                                    w.default)(u + (0,
                                    j.getUuid)() + (0,
                                    j.getUuid)()),
                                    uuid: a
                                },
                                sessionId: (0,
                                j.generateSessionId)().sessionId
                            }
                        } catch (r) {
                            return (0,
                            j.asyncThrowError)(r),
                            {
                                trackCache: {},
                                tlogCookieArr: []
                            }
                        }
                    }
                }, {
                    key: "useAppUuid",
                    value: function() {
                        var r = this;
                        (0,
                        j.checkLiepinApp)() && (0,
                        j.getAppUuid)(function(n) {
                            r.config.uuid = n,
                            r.setConfig(r.config)
                        })
                    }
                }, {
                    key: "deepMerge",
                    value: function(r, n) {
                        try {
                            for (var o in n) {
                                var i, u;
                                null != Object && null !== (i = Object.prototype) && void 0 !== i && null !== (i = i.hasOwnProperty) && void 0 !== i && i.call(n, o) && ((0,
                                j.isObject)(n[o]) && null != r && null !== (u = r.hasOwnProperty) && void 0 !== u && u.call(r, o) && (0,
                                j.isObject)(r[o]) ? r[o] = this.deepMerge(r[o], n[o]) : r[o] = n[o])
                            }
                            return r
                        } catch (n) {
                            return (0,
                            j.asyncThrowError)(n),
                            r
                        }
                    }
                }, {
                    key: "setConfig",
                    value: function(r) {
                        try {
                            this.updateConfig(r),
                            this.client.updateConfig(this.config),
                            this.client.updateModulesConfig(this.config)
                        } catch (r) {
                            (0,
                            j.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "getConfig",
                    value: function(r) {
                        return k(k({}, this.config), r)
                    }
                }, {
                    key: "updateConfig",
                    value: function(r) {
                        this.config = k(k({}, this.config), r)
                    }
                }, {
                    key: "info",
                    value: function() {
                        for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                            i[u] = arguments[u];
                        return (n = this.client.logs).info.apply(n, y(r = ["ConfigManager"]).call(r, i))
                    }
                }, {
                    key: "error",
                    value: function() {
                        for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                            i[u] = arguments[u];
                        return (n = this.client.logs).error.apply(n, y(r = ["ConfigManager"]).call(r, i))
                    }
                }],
                S(s.prototype, o),
                i && S(s, i),
                Object.defineProperty(s, "prototype", {
                    writable: !1
                }),
                s
            }(g.EventEmitter)
        }
    })
      , oe = u({
        "src/builder/trackBuilder.ts": function(r) {
            var n = tw()
              , o = tO()
              , i = tS()
              , u = tC()
              , a = tM()
              , c = tB()
              , s = tH()
              , l = tG()
              , f = tZ();
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.getCustomEventData = E,
            r.getEventData = O,
            r.getPageRefer = _,
            r.getPageReferByInfo = function(r, n) {
                var o = m({
                    pageId: "",
                    elemId: "",
                    cid: "",
                    ctype: "",
                    traceId: ""
                }, n);
                return o.pageId || (o.pageId = g(o.pageId, r)),
                _(b(o.pageId, o.elemId), w(o))
            }
            ,
            r.getSCM = w,
            r.getSCMObj = x,
            r.getSPM = b,
            r.getSPMObj = j,
            r.getTrackData = function() {
                var r = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : {}
                  , n = arguments.length > 1 ? arguments[1] : void 0;
                if (r.type === p.ReportEventType.customEvent)
                    return E(r, n);
                try {
                    var o, i, u, c, s = (0,
                    d.getQuery)("pgRef", location.href), l = (null == r || null === (o = r.pgRefObj) || void 0 === o ? void 0 : o.elemId) || r.traceCode || (null == r || null === (i = r.data_info) || void 0 === i ? void 0 : i.layer_md5) || "", h = m(m(m({}, null == r ? void 0 : r.data_info), null == r || null === (u = r.pgRefObj) || void 0 === u ? void 0 : u.ext), null == r ? void 0 : r.ext);
                    r.page_md5 = n.page_md5,
                    r.session_seq = n.session_seq,
                    r.uuid = n.uuid,
                    r.sessionId = n.sessionId,
                    r.refer = n.refer;
                    var y = {}
                      , g = {};
                    r.traceCode ? y = {
                        page: "sys_page",
                        elem: r.traceCode
                    } : 0 === l.indexOf(p.AUTOTRACK_KEY) && (g = {
                        page: f(b = "".concat(p.AUTOTRACK_KEY)).call(b, null === (w = location.href) || void 0 === w ? void 0 : w.split("?")[0]),
                        elem: l
                    });
                    var b, w, _, T = {
                        pgRef: s,
                        spm: m(m(m({}, g), j(n, {
                            elemId: l
                        })), y),
                        scm: m({}, x(null === (c = r.pgRefObj) || void 0 === c ? void 0 : c.scm)),
                        ext: h
                    }, k = [];
                    return "e" === r.type ? null != r && null !== (_ = r.multiple_exposure) && void 0 !== _ && _.length && r.multiple_exposure.forEach(function(o) {
                        var i, u, a, c = {
                            pgRef: s,
                            spm: m({}, j(n, {
                                elemId: null == o || null === (i = o.pgRefObj) || void 0 === i ? void 0 : i.elemId
                            })),
                            scm: m({}, x(null == o || null === (u = o.pgRefObj) || void 0 === u ? void 0 : u.scm)),
                            ext: m(m(m({}, o.data_info), o.ext), null == o || null === (a = o.pgRefObj) || void 0 === a ? void 0 : a.ext)
                        };
                        k.push(O(m(m({}, r), {}, {
                            eventSeq: o.eventSeq
                        }), c))
                    }) : k = [O(r, T)],
                    k = a(k).call(k, function(r) {
                        return r
                    })
                } catch (r) {
                    return (0,
                    v.asyncThrowError)(r),
                    []
                }
            }
            ;
            var d = nd()
              , p = nI()
              , v = nK();
            function h(r) {
                return (h = "function" == typeof n && "symbol" == typeof o ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof n && r.constructor === n && r !== n.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            function y(r, n) {
                var o = i(r);
                if (u) {
                    var s = u(r);
                    n && (s = a(s).call(s, function(n) {
                        return c(r, n).enumerable
                    })),
                    o.push.apply(o, s)
                }
                return o
            }
            function m(r) {
                for (var n = 1; n < arguments.length; n++) {
                    var o = null != arguments[n] ? arguments[n] : {};
                    n % 2 ? y(Object(o), !0).forEach(function(n) {
                        (function(r, n, o) {
                            var i;
                            (i = function(r, n) {
                                if ("object" != h(r) || !r)
                                    return r;
                                var o = r[l];
                                if (void 0 !== o) {
                                    var i = o.call(r, n || "default");
                                    if ("object" != h(i))
                                        return i;
                                    throw TypeError("@@toPrimitive must return a primitive value.")
                                }
                                return ("string" === n ? String : Number)(r)
                            }(n, "string"),
                            (n = "symbol" == h(i) ? i : i + "")in r) ? Object.defineProperty(r, n, {
                                value: o,
                                enumerable: !0,
                                configurable: !0,
                                writable: !0
                            }) : r[n] = o
                        }
                        )(r, n, o[n])
                    }) : s ? Object.defineProperties(r, s(o)) : y(Object(o)).forEach(function(n) {
                        Object.defineProperty(r, n, c(o, n))
                    })
                }
                return r
            }
            function g(r, n) {
                var o, i, u;
                return r || (null == n ? void 0 : n.pageId) || (null === (i = window.tlg) || void 0 === i ? void 0 : i.pageId) || f(o = "".concat(p.AUTOTRACK_KEY)).call(o, null === (u = location.href) || void 0 === u ? void 0 : u.split("?")[0]) || ""
            }
            function b(r, n) {
                var o, i = g(r);
                return f(o = "".concat(encodeURIComponent(-1 !== (null == i ? void 0 : i.indexOf(p.AUTOTRACK_KEY)) ? "" : i), ":")).call(o, encodeURIComponent((-1 !== (null == n ? void 0 : n.indexOf(p.AUTOTRACK_KEY)) ? "" : n) || ""))
            }
            function j(r, n) {
                var o = m({}, n)
                  , i = o.elemId
                  , u = o.pageId
                  , a = void 0 === u ? "" : u
                  , c = "";
                return a || (c = g(a, r)),
                {
                    page: c || "",
                    elem: (void 0 === i ? "" : i) || ""
                }
            }
            function w(r) {
                var n, o, i = m({}, r), u = i.cid, a = i.traceId, c = i.ctype;
                return f(n = f(o = "".concat(encodeURIComponent(void 0 === u ? "" : u), ":")).call(o, encodeURIComponent(void 0 === c ? "" : c), ":")).call(n, encodeURIComponent(void 0 === a ? "" : a))
            }
            function x(r) {
                var n = m({}, r)
                  , o = n.cid
                  , i = void 0 === o ? "" : o
                  , u = n.ctype
                  , a = void 0 === u ? "" : u
                  , c = n.traceId
                  , s = void 0 === c ? "" : c
                  , l = {};
                return i && (l.cid = i),
                a && (l.ctype = a),
                s && (l.ctraceId = s),
                l
            }
            function _() {
                var r, n = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : "";
                return encodeURIComponent(f(r = "".concat(arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : "", "@")).call(r, n))
            }
            function E(r) {
                var n = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {};
                try {
                    return [{
                        std: {
                            timestamp: (0,
                            d.now)(),
                            sessionId: n.sessionId,
                            eventSeq: r.eventSeq,
                            uuid: n.uuid,
                            url: location.href,
                            refer: decodeURIComponent(n.refer || "")
                        },
                        eventType: p.ReportEventType.customEvent,
                        eventId: r.eventId,
                        ext: m(m({}, r.data_info), r.ext)
                    }]
                } catch (r) {
                    return (0,
                    v.asyncThrowError)(r),
                    null
                }
            }
            function O(r) {
                var n = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {};
                try {
                    return {
                        eventType: r.type,
                        std: {
                            timestamp: (0,
                            d.now)(),
                            sessionId: r.sessionId,
                            eventSeq: r.eventSeq,
                            pgSeq: r.session_seq,
                            uuid: r.uuid,
                            pageMd5: r.page_md5,
                            url: location.href,
                            refer: decodeURIComponent(r.refer || "")
                        },
                        spm: m({}, n.spm),
                        scm: m({}, n.scm),
                        pgRef: n.pgRef || "",
                        ext: m(m({}, r.data_info), n.ext)
                    }
                } catch (r) {
                    return (0,
                    v.asyncThrowError)(r),
                    null
                }
            }
        }
    })
      , ot = u({
        "src/builder/commonBuilder.ts": function(r) {
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.getCommonInfo = function(r, n) {
                var o, i;
                return {
                    resolution: n.resolution || "0X0",
                    businessId: (null == r || null === (o = r.payload) || void 0 === o ? void 0 : o.accountId) || (null == n ? void 0 : n.accountId) || (null === (i = window) || void 0 === i || null === (i = i.tlg) || void 0 === i ? void 0 : i.accountId) || ""
                }
            }
        }
    })
      , or = u({
        "src/builder/index.ts": function(r) {
            var o = tw()
              , i = tO()
              , u = tS()
              , a = tC()
              , c = tM()
              , s = tB()
              , l = tH()
              , f = tX()
              , d = t2()
              , p = tG()
              , v = tZ();
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.defaultConfig = r.Builder = void 0;
            var h = nK()
              , y = nI()
              , m = oe()
              , g = ot();
            function b(r) {
                return (b = "function" == typeof o && "symbol" == typeof i ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof o && r.constructor === o && r !== o.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            function j(r, n) {
                var o = u(r);
                if (a) {
                    var i = a(r);
                    n && (i = c(i).call(i, function(n) {
                        return s(r, n).enumerable
                    })),
                    o.push.apply(o, i)
                }
                return o
            }
            function w(r) {
                for (var n = 1; n < arguments.length; n++) {
                    var o = null != arguments[n] ? arguments[n] : {};
                    n % 2 ? j(Object(o), !0).forEach(function(n) {
                        T(r, n, o[n])
                    }) : l ? Object.defineProperties(r, l(o)) : j(Object(o)).forEach(function(n) {
                        Object.defineProperty(r, n, s(o, n))
                    })
                }
                return r
            }
            function x(r, n) {
                for (var o = 0; o < n.length; o++) {
                    var i = n[o];
                    i.enumerable = i.enumerable || !1,
                    i.configurable = !0,
                    "value"in i && (i.writable = !0),
                    Object.defineProperty(r, k(i.key), i)
                }
            }
            function _() {
                try {
                    var r = !Boolean.prototype.valueOf.call(f(Boolean, [], function() {}))
                } catch (r) {}
                return (_ = function() {
                    return !!r
                }
                )()
            }
            function E(r) {
                return (E = Object.setPrototypeOf ? d.bind() : function(r) {
                    return r.__proto__ || d(r)
                }
                )(r)
            }
            function O(r, n) {
                return (O = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(r, n) {
                    return r.__proto__ = n,
                    r
                }
                )(r, n)
            }
            function T(r, n, o) {
                return (n = k(n))in r ? Object.defineProperty(r, n, {
                    value: o,
                    enumerable: !0,
                    configurable: !0,
                    writable: !0
                }) : r[n] = o,
                r
            }
            function k(r) {
                var n = function(r, n) {
                    if ("object" != b(r) || !r)
                        return r;
                    var o = r[p];
                    if (void 0 !== o) {
                        var i = o.call(r, n || "default");
                        if ("object" != b(i))
                            return i;
                        throw TypeError("@@toPrimitive must return a primitive value.")
                    }
                    return ("string" === n ? String : Number)(r)
                }(r, "string");
                return "symbol" == b(n) ? n : n + ""
            }
            r.defaultConfig = {},
            r.Builder = function(r) {
                var o, i;
                function u(r, o) {
                    var i, a, c;
                    return function(r, o) {
                        if (!n(r, o))
                            throw TypeError("Cannot call a class as a function")
                    }(this, u),
                    T((a = E(a = u),
                    i = function(r, n) {
                        if (n && ("object" == b(n) || "function" == typeof n))
                            return n;
                        if (void 0 !== n)
                            throw TypeError("Derived constructors may only return object or undefined");
                        return function(r) {
                            if (void 0 === r)
                                throw ReferenceError("this hasn't been initialised - super() hasn't been called");
                            return r
                        }(r)
                    }(this, _() ? f(a, [], E(this).constructor) : a.apply(this, c))), "config", {}),
                    i.client = r,
                    i.config = w({}, o),
                    i.info("builder 初始化"),
                    i
                }
                return function(r, n) {
                    if ("function" != typeof n && null !== n)
                        throw TypeError("Super expression must either be null or a function");
                    r.prototype = Object.create(n && n.prototype, {
                        constructor: {
                            value: r,
                            writable: !0,
                            configurable: !0
                        }
                    }),
                    Object.defineProperty(r, "prototype", {
                        writable: !1
                    }),
                    n && O(r, n)
                }(u, r),
                o = [{
                    key: "build",
                    value: function(r, n) {
                        try {
                            this.info("开始格式化数据 config", n);
                            var o = r.payload
                              , i = (0,
                            m.getTrackData)(o, this.config) || [];
                            return {
                                data: {
                                    commonInfo: w({}, (0,
                                    g.getCommonInfo)(r, this.client.config)),
                                    ver: y.TLOG_VERSION_KEY,
                                    events: i
                                }
                            }
                        } catch (r) {
                            return (0,
                            h.asyncThrowError)(r),
                            null
                        }
                    }
                }, {
                    key: "report",
                    value: function(r, n) {
                        try {
                            this.emit(y.LifecycleEvent.beforeBuild, r);
                            var o, i = this.build(r, n);
                            this.emit(y.LifecycleEvent.build, i),
                            i && null !== (o = i.data.events) && void 0 !== o && o.length ? (this.info("格式化数据完成 data", i),
                            this.client.send(i)) : this.error("格式化数据失败", i)
                        } catch (r) {
                            (0,
                            h.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "info",
                    value: function() {
                        for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                            i[u] = arguments[u];
                        return (n = this.client.logs).info.apply(n, v(r = ["builder"]).call(r, i))
                    }
                }, {
                    key: "error",
                    value: function() {
                        for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                            i[u] = arguments[u];
                        return (n = this.client.logs).error.apply(n, v(r = ["builder"]).call(r, i))
                    }
                }, {
                    key: "updateConfig",
                    value: function(r) {
                        this.config = w(w({}, this.config), r)
                    }
                }],
                x(u.prototype, o),
                i && x(u, i),
                Object.defineProperty(u, "prototype", {
                    writable: !1
                }),
                u
            }(h.EventEmitter)
        }
    })
      , on = u({
        "node_modules/core-js-pure/modules/es.array.find.js": function() {
            var r = et()
              , n = eH().find
              , o = ti()
              , i = "find"
              , u = !0;
            i in [] && [, ][i](function() {
                u = !1
            }),
            r({
                target: "Array",
                proto: !0,
                forced: u
            }, {
                find: function(r) {
                    return n(this, r, arguments.length > 1 ? arguments[1] : void 0)
                }
            }),
            o(i)
        }
    })
      , oo = u({
        "node_modules/core-js-pure/es/array/virtual/find.js": function(r, n) {
            on(),
            n.exports = tI()("Array", "find")
        }
    })
      , oi = u({
        "node_modules/core-js-pure/es/instance/find.js": function(r, n) {
            var o = T()
              , i = oo()
              , u = Array.prototype;
            n.exports = function(r) {
                var n = r.find;
                return r === u || o(u, r) && n === u.find ? i : n
            }
        }
    })
      , ou = u({
        "node_modules/core-js-pure/stable/instance/find.js": function(r, n) {
            n.exports = oi()
        }
    })
      , oa = u({
        "node_modules/core-js-pure/internals/collection-strong.js": function(r, n) {
            var o = eS()
              , i = eL()
              , u = nh()
              , a = X()
              , c = rh()
              , s = j()
              , l = rc()
              , f = ty()
              , d = tm()
              , p = rv()
              , v = h()
              , y = ng().fastKey
              , m = eq()
              , g = m.set
              , b = m.getterFor;
            n.exports = {
                getConstructor: function(r, n, f, d) {
                    var p = r(function(r, i) {
                        c(r, h),
                        g(r, {
                            type: n,
                            index: o(null),
                            first: null,
                            last: null,
                            size: 0
                        }),
                        v || (r.size = 0),
                        s(i) || l(i, r[d], {
                            that: r,
                            AS_ENTRIES: f
                        })
                    })
                      , h = p.prototype
                      , m = b(n)
                      , j = function(r, n, o) {
                        var i, u, a = m(r), c = w(r, n);
                        return c ? c.value = o : (a.last = c = {
                            index: u = y(n, !0),
                            key: n,
                            value: o,
                            previous: i = a.last,
                            next: null,
                            removed: !1
                        },
                        a.first || (a.first = c),
                        i && (i.next = c),
                        v ? a.size++ : r.size++,
                        "F" !== u && (a.index[u] = c)),
                        r
                    }
                      , w = function(r, n) {
                        var o, i = m(r), u = y(n);
                        if ("F" !== u)
                            return i.index[u];
                        for (o = i.first; o; o = o.next)
                            if (o.key === n)
                                return o
                    };
                    return u(h, {
                        clear: function() {
                            for (var r = m(this), n = r.first; n; )
                                n.removed = !0,
                                n.previous && (n.previous = n.previous.next = null),
                                n = n.next;
                            r.first = r.last = null,
                            r.index = o(null),
                            v ? r.size = 0 : this.size = 0
                        },
                        delete: function(r) {
                            var n = m(this)
                              , o = w(this, r);
                            if (o) {
                                var i = o.next
                                  , u = o.previous;
                                delete n.index[o.index],
                                o.removed = !0,
                                u && (u.next = i),
                                i && (i.previous = u),
                                n.first === o && (n.first = i),
                                n.last === o && (n.last = u),
                                v ? n.size-- : this.size--
                            }
                            return !!o
                        },
                        forEach: function(r) {
                            for (var n, o = m(this), i = a(r, arguments.length > 1 ? arguments[1] : void 0); n = n ? n.next : o.first; )
                                for (i(n.value, n.key, this); n && n.removed; )
                                    n = n.previous
                        },
                        has: function(r) {
                            return !!w(this, r)
                        }
                    }),
                    u(h, f ? {
                        get: function(r) {
                            var n = w(this, r);
                            return n && n.value
                        },
                        set: function(r, n) {
                            return j(this, 0 === r ? 0 : r, n)
                        }
                    } : {
                        add: function(r) {
                            return j(this, r = 0 === r ? 0 : r, r)
                        }
                    }),
                    v && i(h, "size", {
                        configurable: !0,
                        get: function() {
                            return m(this).size
                        }
                    }),
                    p
                },
                setStrong: function(r, n, o) {
                    var i = n + " Iterator"
                      , u = b(n)
                      , a = b(i);
                    f(r, n, function(r, n) {
                        g(this, {
                            type: i,
                            target: r,
                            state: u(r),
                            kind: n,
                            last: null
                        })
                    }, function() {
                        for (var r = a(this), n = r.kind, o = r.last; o && o.removed; )
                            o = o.previous;
                        return r.target && (r.last = o = o ? o.next : r.state.first) ? d("keys" === n ? o.key : "values" === n ? o.value : [o.key, o.value], !1) : (r.target = null,
                        d(void 0, !0))
                    }, o ? "entries" : "values", !o, !0),
                    p(n)
                }
            }
        }
    })
      , oc = u({
        "node_modules/core-js-pure/modules/es.map.constructor.js": function() {
            nb()("Map", function(r) {
                return function() {
                    return r(this, arguments.length ? arguments[0] : void 0)
                }
            }, oa())
        }
    })
      , os = u({
        "node_modules/core-js-pure/modules/es.map.js": function() {
            oc()
        }
    })
      , ol = u({
        "node_modules/core-js-pure/internals/caller.js": function(r, n) {
            n.exports = function(r, n) {
                return 1 === n ? function(n, o) {
                    return n[r](o)
                }
                : function(n, o, i) {
                    return n[r](o, i)
                }
            }
        }
    })
      , of = u({
        "node_modules/core-js-pure/internals/map-helpers.js": function(r, n) {
            var o = O()
              , i = ol()
              , u = o("Map");
            n.exports = {
                Map: u,
                set: i("set", 2),
                get: i("get", 1),
                has: i("has", 1),
                remove: i("delete", 1),
                proto: u.prototype
            }
        }
    })
      , od = u({
        "node_modules/core-js-pure/modules/es.map.group-by.js": function() {
            var r = et()
              , n = f()
              , o = R()
              , i = w()
              , u = rc()
              , a = of()
              , s = N()
              , l = c()
              , d = a.Map
              , p = a.has
              , v = a.get
              , h = a.set
              , y = n([].push)
              , m = s || l(function() {
                return 1 !== d.groupBy("ab", function(r) {
                    return r
                }).get("a").length
            });
            r({
                target: "Map",
                stat: !0,
                forced: s || m
            }, {
                groupBy: function(r, n) {
                    i(r),
                    o(n);
                    var a = new d
                      , c = 0;
                    return u(r, function(r) {
                        var o = n(r, c++);
                        p(a, o) ? y(v(a, o), r) : h(a, o, [r])
                    }),
                    a
                }
            })
        }
    })
      , op = u({
        "node_modules/core-js-pure/es/map/index.js": function(r, n) {
            tg(),
            os(),
            od(),
            em(),
            t_(),
            n.exports = E().Map
        }
    })
      , ov = u({
        "node_modules/core-js-pure/stable/map/index.js": function(r, n) {
            var o = op();
            tj(),
            n.exports = o
        }
    })
      , oh = u({
        "node_modules/core-js-pure/es/array/virtual/entries.js": function(r, n) {
            tg(),
            em(),
            n.exports = tI()("Array", "entries")
        }
    })
      , oy = u({
        "node_modules/core-js-pure/stable/array/virtual/entries.js": function(r, n) {
            n.exports = oh()
        }
    })
      , om = u({
        "node_modules/core-js-pure/stable/instance/entries.js": function(r, n) {
            tj();
            var o = el()
              , i = q()
              , u = T()
              , a = oy()
              , c = Array.prototype
              , s = {
                DOMTokenList: !0,
                NodeList: !0
            };
            n.exports = function(r) {
                var n = r.entries;
                return r === c || u(c, r) && n === c.entries || i(s, o(r)) ? a : n
            }
        }
    })
      , og = u({
        "src/common/request.ts": function(r) {
            var o = tw()
              , i = t2()
              , u = rG()
              , a = r2()
              , c = ns()
              , s = tO()
              , l = r8()
              , f = tS()
              , d = tC()
              , p = tM()
              , v = tB()
              , h = tH()
              , y = tG()
              , m = t7()
              , g = ov()
              , b = n5()
              , j = nA()
              , w = om();
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.ajax = M,
            r.beacon = function(r, n) {
                if (!navigator.sendBeacon)
                    return null;
                var o = "";
                return o = (0,
                x.isString)(n) ? n : (0,
                x.param)(n),
                navigator.sendBeacon(r, o)
            }
            ,
            r.buildFscpHeader = I,
            r.buildHeaders = R,
            r.get = N,
            r.getJSON = function(r) {
                return B.apply(this, arguments)
            }
            ,
            r.parseResponseHeaders = L,
            r.post = U,
            r.postJSON = function(r) {
                return q.apply(this, arguments)
            }
            ;
            var x = nd();
            function _() {
                _ = function() {
                    return c
                }
                ;
                var r, c = {}, s = Object.prototype, l = s.hasOwnProperty, f = Object.defineProperty || function(r, n, o) {
                    r[n] = o.value
                }
                , d = "function" == typeof o ? o : {}, p = d.iterator || "@@iterator", v = d.asyncIterator || "@@asyncIterator", h = d.toStringTag || "@@toStringTag";
                function y(r, n, o) {
                    return Object.defineProperty(r, n, {
                        value: o,
                        enumerable: !0,
                        configurable: !0,
                        writable: !0
                    }),
                    r[n]
                }
                try {
                    y({}, "")
                } catch (r) {
                    y = function(r, n, o) {
                        return r[n] = o
                    }
                }
                function m(o, i, u, a) {
                    var c, s, l, d, p = Object.create((i && n(i.prototype, E) ? i : E).prototype);
                    return f(p, "_invoke", {
                        value: (c = o,
                        s = u,
                        l = new M(a || []),
                        d = b,
                        function(n, o) {
                            if (d === j)
                                throw Error("Generator is already running");
                            if (d === w) {
                                if ("throw" === n)
                                    throw o;
                                return {
                                    value: r,
                                    done: !0
                                }
                            }
                            for (l.method = n,
                            l.arg = o; ; ) {
                                var i = l.delegate;
                                if (i) {
                                    var u = function n(o, i) {
                                        var u = i.method
                                          , a = o.iterator[u];
                                        if (a === r)
                                            return i.delegate = null,
                                            "throw" === u && o.iterator.return && (i.method = "return",
                                            i.arg = r,
                                            n(o, i),
                                            "throw" === i.method) || "return" !== u && (i.method = "throw",
                                            i.arg = TypeError("The iterator does not provide a '" + u + "' method")),
                                            x;
                                        var c = g(a, o.iterator, i.arg);
                                        if ("throw" === c.type)
                                            return i.method = "throw",
                                            i.arg = c.arg,
                                            i.delegate = null,
                                            x;
                                        var s = c.arg;
                                        return s ? s.done ? (i[o.resultName] = s.value,
                                        i.next = o.nextLoc,
                                        "return" !== i.method && (i.method = "next",
                                        i.arg = r),
                                        i.delegate = null,
                                        x) : s : (i.method = "throw",
                                        i.arg = TypeError("iterator result is not an object"),
                                        i.delegate = null,
                                        x)
                                    }(i, l);
                                    if (u) {
                                        if (u === x)
                                            continue;
                                        return u
                                    }
                                }
                                if ("next" === l.method)
                                    l.sent = l._sent = l.arg;
                                else if ("throw" === l.method) {
                                    if (d === b)
                                        throw d = w,
                                        l.arg;
                                    l.dispatchException(l.arg)
                                } else
                                    "return" === l.method && l.abrupt("return", l.arg);
                                d = j;
                                var a = g(c, s, l);
                                if ("normal" === a.type) {
                                    if (d = l.done ? w : "suspendedYield",
                                    a.arg === x)
                                        continue;
                                    return {
                                        value: a.arg,
                                        done: l.done
                                    }
                                }
                                "throw" === a.type && (d = w,
                                l.method = "throw",
                                l.arg = a.arg)
                            }
                        }
                        )
                    }),
                    p
                }
                function g(r, n, o) {
                    try {
                        return {
                            type: "normal",
                            arg: r.call(n, o)
                        }
                    } catch (r) {
                        return {
                            type: "throw",
                            arg: r
                        }
                    }
                }
                c.wrap = m;
                var b = "suspendedStart"
                  , j = "executing"
                  , w = "completed"
                  , x = {};
                function E() {}
                function O() {}
                function k() {}
                var S = {};
                y(S, p, function() {
                    return this
                });
                var P = i && i(i(N([])));
                P && P !== s && l.call(P, p) && (S = P);
                var C = k.prototype = E.prototype = Object.create(S);
                function A(r) {
                    ["next", "throw", "return"].forEach(function(n) {
                        y(r, n, function(r) {
                            return this._invoke(n, r)
                        })
                    })
                }
                function I(r, n) {
                    var o;
                    f(this, "_invoke", {
                        value: function(i, u) {
                            function a() {
                                return new n(function(o, a) {
                                    (function o(i, u, a, c) {
                                        var s = g(r[i], r, u);
                                        if ("throw" !== s.type) {
                                            var f = s.arg
                                              , d = f.value;
                                            return d && "object" == T(d) && l.call(d, "__await") ? n.resolve(d.__await).then(function(r) {
                                                o("next", r, a, c)
                                            }, function(r) {
                                                o("throw", r, a, c)
                                            }) : n.resolve(d).then(function(r) {
                                                f.value = r,
                                                a(f)
                                            }, function(r) {
                                                return o("throw", r, a, c)
                                            })
                                        }
                                        c(s.arg)
                                    }
                                    )(i, u, o, a)
                                }
                                )
                            }
                            return o = o ? o.then(a, a) : a()
                        }
                    })
                }
                function R(r) {
                    var n = {
                        tryLoc: r[0]
                    };
                    1 in r && (n.catchLoc = r[1]),
                    2 in r && (n.finallyLoc = r[2],
                    n.afterLoc = r[3]),
                    this.tryEntries.push(n)
                }
                function L(r) {
                    var n = r.completion || {};
                    n.type = "normal",
                    delete n.arg,
                    r.completion = n
                }
                function M(r) {
                    this.tryEntries = [{
                        tryLoc: "root"
                    }],
                    r.forEach(R, this),
                    this.reset(!0)
                }
                function N(n) {
                    if (n || "" === n) {
                        var o = n[p];
                        if (o)
                            return o.call(n);
                        if ("function" == typeof n.next)
                            return n;
                        if (!isNaN(n.length)) {
                            var i = -1
                              , u = function o() {
                                for (; ++i < n.length; )
                                    if (l.call(n, i))
                                        return o.value = n[i],
                                        o.done = !1,
                                        o;
                                return o.value = r,
                                o.done = !0,
                                o
                            };
                            return u.next = u
                        }
                    }
                    throw TypeError(T(n) + " is not iterable")
                }
                return O.prototype = k,
                f(C, "constructor", {
                    value: k,
                    configurable: !0
                }),
                f(k, "constructor", {
                    value: O,
                    configurable: !0
                }),
                O.displayName = y(k, h, "GeneratorFunction"),
                c.isGeneratorFunction = function(r) {
                    var n = "function" == typeof r && r.constructor;
                    return !!n && (n === O || "GeneratorFunction" === (n.displayName || n.name))
                }
                ,
                c.mark = function(r) {
                    return Object.setPrototypeOf ? Object.setPrototypeOf(r, k) : (r.__proto__ = k,
                    y(r, h, "GeneratorFunction")),
                    r.prototype = Object.create(C),
                    r
                }
                ,
                c.awrap = function(r) {
                    return {
                        __await: r
                    }
                }
                ,
                A(I.prototype),
                y(I.prototype, v, function() {
                    return this
                }),
                c.AsyncIterator = I,
                c.async = function(r, n, o, i, a) {
                    void 0 === a && (a = u);
                    var s = new I(m(r, n, o, i),a);
                    return c.isGeneratorFunction(n) ? s : s.next().then(function(r) {
                        return r.done ? r.value : s.next()
                    })
                }
                ,
                A(C),
                y(C, h, "Generator"),
                y(C, p, function() {
                    return this
                }),
                y(C, "toString", function() {
                    return "[object Generator]"
                }),
                c.keys = function(r) {
                    var n = Object(r)
                      , o = [];
                    for (var i in n)
                        o.push(i);
                    return o.reverse(),
                    function r() {
                        for (; o.length; ) {
                            var i = o.pop();
                            if (i in n)
                                return r.value = i,
                                r.done = !1,
                                r
                        }
                        return r.done = !0,
                        r
                    }
                }
                ,
                c.values = N,
                M.prototype = {
                    constructor: M,
                    reset: function(n) {
                        if (this.prev = 0,
                        this.next = 0,
                        this.sent = this._sent = r,
                        this.done = !1,
                        this.delegate = null,
                        this.method = "next",
                        this.arg = r,
                        this.tryEntries.forEach(L),
                        !n)
                            for (var o in this)
                                "t" === o.charAt(0) && l.call(this, o) && !isNaN(+a(o).call(o, 1)) && (this[o] = r)
                    },
                    stop: function() {
                        this.done = !0;
                        var r = this.tryEntries[0].completion;
                        if ("throw" === r.type)
                            throw r.arg;
                        return this.rval
                    },
                    dispatchException: function(n) {
                        if (this.done)
                            throw n;
                        var o = this;
                        function i(i, u) {
                            return c.type = "throw",
                            c.arg = n,
                            o.next = i,
                            u && (o.method = "next",
                            o.arg = r),
                            !!u
                        }
                        for (var u = this.tryEntries.length - 1; u >= 0; --u) {
                            var a = this.tryEntries[u]
                              , c = a.completion;
                            if ("root" === a.tryLoc)
                                return i("end");
                            if (a.tryLoc <= this.prev) {
                                var s = l.call(a, "catchLoc")
                                  , f = l.call(a, "finallyLoc");
                                if (s && f) {
                                    if (this.prev < a.catchLoc)
                                        return i(a.catchLoc, !0);
                                    if (this.prev < a.finallyLoc)
                                        return i(a.finallyLoc)
                                } else if (s) {
                                    if (this.prev < a.catchLoc)
                                        return i(a.catchLoc, !0)
                                } else {
                                    if (!f)
                                        throw Error("try statement without catch or finally");
                                    if (this.prev < a.finallyLoc)
                                        return i(a.finallyLoc)
                                }
                            }
                        }
                    },
                    abrupt: function(r, n) {
                        for (var o = this.tryEntries.length - 1; o >= 0; --o) {
                            var i = this.tryEntries[o];
                            if (i.tryLoc <= this.prev && l.call(i, "finallyLoc") && this.prev < i.finallyLoc) {
                                var u = i;
                                break
                            }
                        }
                        u && ("break" === r || "continue" === r) && u.tryLoc <= n && n <= u.finallyLoc && (u = null);
                        var a = u ? u.completion : {};
                        return a.type = r,
                        a.arg = n,
                        u ? (this.method = "next",
                        this.next = u.finallyLoc,
                        x) : this.complete(a)
                    },
                    complete: function(r, n) {
                        if ("throw" === r.type)
                            throw r.arg;
                        return "break" === r.type || "continue" === r.type ? this.next = r.arg : "return" === r.type ? (this.rval = this.arg = r.arg,
                        this.method = "return",
                        this.next = "end") : "normal" === r.type && n && (this.next = n),
                        x
                    },
                    finish: function(r) {
                        for (var n = this.tryEntries.length - 1; n >= 0; --n) {
                            var o = this.tryEntries[n];
                            if (o.finallyLoc === r)
                                return this.complete(o.completion, o.afterLoc),
                                L(o),
                                x
                        }
                    },
                    catch: function(r) {
                        for (var n = this.tryEntries.length - 1; n >= 0; --n) {
                            var o = this.tryEntries[n];
                            if (o.tryLoc === r) {
                                var i = o.completion;
                                if ("throw" === i.type) {
                                    var u = i.arg;
                                    L(o)
                                }
                                return u
                            }
                        }
                        throw Error("illegal catch attempt")
                    },
                    delegateYield: function(n, o, i) {
                        return this.delegate = {
                            iterator: N(n),
                            resultName: o,
                            nextLoc: i
                        },
                        "next" === this.method && (this.arg = r),
                        x
                    }
                },
                c
            }
            function E(r, n, o, i, a, c, s) {
                try {
                    var l = r[c](s)
                      , f = l.value
                } catch (r) {
                    return void o(r)
                }
                l.done ? n(f) : u.resolve(f).then(i, a)
            }
            function O(r) {
                return function() {
                    var n = this
                      , o = arguments;
                    return new u(function(i, u) {
                        var a = r.apply(n, o);
                        function c(r) {
                            E(a, i, u, c, s, "next", r)
                        }
                        function s(r) {
                            E(a, i, u, c, s, "throw", r)
                        }
                        c(void 0)
                    }
                    )
                }
            }
            function T(r) {
                return (T = "function" == typeof o && "symbol" == typeof s ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof o && r.constructor === o && r !== o.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            function k(r, n) {
                var i = void 0 !== o && c(r) || r["@@iterator"];
                if (!i) {
                    if (Array.isArray(r) || (i = S(r)) || n && r && "number" == typeof r.length) {
                        i && (r = i);
                        var u = 0
                          , a = function() {};
                        return {
                            s: a,
                            n: function() {
                                return u >= r.length ? {
                                    done: !0
                                } : {
                                    done: !1,
                                    value: r[u++]
                                }
                            },
                            e: function(r) {
                                throw r
                            },
                            f: a
                        }
                    }
                    throw TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")
                }
                var s, l = !0, f = !1;
                return {
                    s: function() {
                        i = i.call(r)
                    },
                    n: function() {
                        var r = i.next();
                        return l = r.done,
                        r
                    },
                    e: function(r) {
                        f = !0,
                        s = r
                    },
                    f: function() {
                        try {
                            l || null == i.return || i.return()
                        } finally {
                            if (f)
                                throw s
                        }
                    }
                }
            }
            function S(r, n) {
                if (r) {
                    if ("string" == typeof r)
                        return P(r, n);
                    var o, i = a(o = ({}).toString.call(r)).call(o, 8, -1);
                    return "Object" === i && r.constructor && (i = r.constructor.name),
                    "Map" === i || "Set" === i ? l(r) : "Arguments" === i || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i) ? P(r, n) : void 0
                }
            }
            function P(r, n) {
                (null == n || n > r.length) && (n = r.length);
                for (var o = 0, i = Array(n); o < n; o++)
                    i[o] = r[o];
                return i
            }
            function C(r, n) {
                var o = f(r);
                if (d) {
                    var i = d(r);
                    n && (i = p(i).call(i, function(n) {
                        return v(r, n).enumerable
                    })),
                    o.push.apply(o, i)
                }
                return o
            }
            function A(r) {
                for (var n = 1; n < arguments.length; n++) {
                    var o = null != arguments[n] ? arguments[n] : {};
                    n % 2 ? C(Object(o), !0).forEach(function(n) {
                        (function(r, n, o) {
                            var i;
                            (i = function(r, n) {
                                if ("object" != T(r) || !r)
                                    return r;
                                var o = r[y];
                                if (void 0 !== o) {
                                    var i = o.call(r, n || "default");
                                    if ("object" != T(i))
                                        return i;
                                    throw TypeError("@@toPrimitive must return a primitive value.")
                                }
                                return ("string" === n ? String : Number)(r)
                            }(n, "string"),
                            (n = "symbol" == T(i) ? i : i + "")in r) ? Object.defineProperty(r, n, {
                                value: o,
                                enumerable: !0,
                                configurable: !0,
                                writable: !0
                            }) : r[n] = o
                        }
                        )(r, n, o[n])
                    }) : h ? Object.defineProperties(r, h(o)) : C(Object(o)).forEach(function(n) {
                        Object.defineProperty(r, n, v(o, n))
                    })
                }
                return r
            }
            function I() {
                var r = (arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : {}).biStat
                  , n = void 0 === r ? {} : r
                  , o = {};
                return window && !n.location && (o = A(A({}, n), {}, {
                    location: "".concat(window.location.href)
                })),
                {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-Client-Type": "web",
                    "X-Fscp-Bi-Stat": m(o),
                    "X-Fscp-Std-Info": m({
                        client_id: window.__FE_CLIENT_ID
                    }),
                    "X-Fscp-Trace-Id": (0,
                    x.uuidV4)(),
                    "X-Fscp-Version": "1.1"
                }
            }
            function R(r) {
                var n = new g;
                if (!r)
                    return n;
                for (var o = 0, i = f(r); o < i.length; o++) {
                    var u = i[o];
                    n.set(u, "".concat(r[u]))
                }
                return n
            }
            function L(r) {
                var n = {};
                if (!r)
                    return n;
                var o, i = k(r.split(/\r\n/g));
                try {
                    for (i.s(); !(o = i.n()).done; ) {
                        var u, c, s = o.value, l = s.split(/:/g)[0];
                        l && b(n, l, j(u = a(c = s.split(/:/g)).call(c, 1).join(":")).call(u))
                    }
                } catch (r) {
                    i.e(r)
                } finally {
                    i.f()
                }
                return n
            }
            function M(r, n) {
                var i = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : {}
                  , a = i.headers
                  , s = i.body;
                return new u(function(i, u) {
                    try {
                        var l = window.XMLHttpRequest ? new XMLHttpRequest : null;
                        if (null === l)
                            throw Error("初始化 XMLHttpRequest 失败");
                        l.withCredentials = !0,
                        l.onload = function() {
                            var r = {
                                status: l.status,
                                body: l.responseText,
                                json: function(r, n) {
                                    try {
                                        var o = r.getAllResponseHeaders();
                                        return o && -1 !== o.indexOf("application/json") ? JSON.parse(n) : n
                                    } catch (r) {
                                        return null
                                    }
                                }(l, l.responseText),
                                responseHeaders: l.getAllResponseHeaders(),
                                requestHeaders: a,
                                headers: L(l.getAllResponseHeaders()),
                                xhr: l
                            };
                            return 199 < l.status && l.status < 300 ? i(r) : u(r)
                        }
                        ,
                        l.open(r, n);
                        var f = "";
                        if (a) {
                            var d, p, v = R(a), h = k(w(v).call(v));
                            try {
                                for (h.s(); !(p = h.n()).done; ) {
                                    var y, g = (y = p.value,
                                    function(r) {
                                        if (Array.isArray(r))
                                            return r
                                    }(y) || function(r, n) {
                                        var i = null == r ? null : void 0 !== o && c(r) || r["@@iterator"];
                                        if (null != i) {
                                            var u, a, s, l, f = [], d = !0, p = !1;
                                            try {
                                                s = (i = i.call(r)).next,
                                                !1;
                                                for (; !(d = (u = s.call(i)).done) && (f.push(u.value),
                                                f.length !== n); d = !0)
                                                    ;
                                            } catch (r) {
                                                p = !0,
                                                a = r
                                            } finally {
                                                try {
                                                    if (!d && null != i.return && (l = i.return(),
                                                    Object(l) !== l))
                                                        return
                                                } finally {
                                                    if (p)
                                                        throw a
                                                }
                                            }
                                            return f
                                        }
                                    }(y, 2) || S(y, 2) || function() {
                                        throw TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")
                                    }()), b = g[0], j = g[1];
                                    l.setRequestHeader(b.toLowerCase(), j)
                                }
                            } catch (r) {
                                h.e(r)
                            } finally {
                                h.f()
                            }
                            (v.get("Content-Type") && -1 !== (null === (d = v.get("Content-Type")) || void 0 === d ? void 0 : d.indexOf("application/json")) || "object" === T(s)) && (f = m(s))
                        }
                        s && 0 === f.length && (f = (0,
                        x.param)(s)),
                        l.send(f)
                    } catch (r) {
                        u(r)
                    }
                }
                )
            }
            function N(r) {
                return D.apply(this, arguments)
            }
            function D() {
                return (D = O(_().mark(function r(n) {
                    var o, i = arguments;
                    return _().wrap(function(r) {
                        for (; ; )
                            switch (r.prev = r.next) {
                            case 0:
                                return o = (i.length > 1 && void 0 !== i[1] ? i[1] : {}).headers,
                                r.next = 3,
                                M("GET", n, {
                                    headers: o
                                });
                            case 3:
                                return r.abrupt("return", r.sent);
                            case 4:
                            case "end":
                                return r.stop()
                            }
                    }, r)
                }))).apply(this, arguments)
            }
            function B() {
                return (B = O(_().mark(function r(n) {
                    var o, i = arguments;
                    return _().wrap(function(r) {
                        for (; ; )
                            switch (r.prev = r.next) {
                            case 0:
                                return o = A(A({}, (i.length > 1 && void 0 !== i[1] ? i[1] : {}).headers), {}, {
                                    "Content-Type": "application/json"
                                }, I()),
                                r.next = 4,
                                N(n, {
                                    headers: o
                                });
                            case 4:
                                return r.abrupt("return", r.sent.json);
                            case 5:
                            case "end":
                                return r.stop()
                            }
                    }, r)
                }))).apply(this, arguments)
            }
            function U(r) {
                return F.apply(this, arguments)
            }
            function F() {
                return (F = O(_().mark(function r(n) {
                    var o, i, u, a, c, s = arguments;
                    return _().wrap(function(r) {
                        for (; ; )
                            switch (r.prev = r.next) {
                            case 0:
                                return i = (o = s.length > 1 && void 0 !== s[1] ? s[1] : {}).headers,
                                u = o.body,
                                a = o.fscpOpt,
                                c = A(A(A({}, i), I(a)), {}, {
                                    "Content-Type": "application/json; charset=UTF-8"
                                }),
                                r.next = 4,
                                M("POST", n, {
                                    headers: c,
                                    body: u
                                });
                            case 4:
                                return r.abrupt("return", r.sent);
                            case 5:
                            case "end":
                                return r.stop()
                            }
                    }, r)
                }))).apply(this, arguments)
            }
            function q() {
                return (q = O(_().mark(function r(n) {
                    var o, i, u, a, c, s = arguments;
                    return _().wrap(function(r) {
                        for (; ; )
                            switch (r.prev = r.next) {
                            case 0:
                                return i = (o = s.length > 1 && void 0 !== s[1] ? s[1] : {}).headers,
                                u = o.body,
                                a = o.fscpOpt,
                                c = A(A(A({}, i), I(a)), {}, {
                                    "Content-Type": "application/json; charset=UTF-8"
                                }),
                                r.next = 4,
                                U(n, {
                                    headers: c,
                                    body: u
                                });
                            case 4:
                                return r.abrupt("return", r.sent);
                            case 5:
                            case "end":
                                return r.stop()
                            }
                    }, r)
                }))).apply(this, arguments)
            }
        }
    })
      , ob = u({
        "src/sender/index.ts": function(r) {
            var o = tw()
              , i = tO()
              , u = t2()
              , a = rG()
              , c = r2()
              , s = tS()
              , l = tC()
              , f = tM()
              , d = tB()
              , p = tH()
              , v = tX()
              , h = tG()
              , y = ou()
              , m = r$()
              , g = tZ();
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.Sender = void 0;
            var b = nd()
              , j = og()
              , w = nK()
              , x = nI();
            function _(r) {
                return (_ = "function" == typeof o && "symbol" == typeof i ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof o && r.constructor === o && r !== o.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            function E() {
                E = function() {
                    return i
                }
                ;
                var r, i = {}, s = Object.prototype, l = s.hasOwnProperty, f = Object.defineProperty || function(r, n, o) {
                    r[n] = o.value
                }
                , d = "function" == typeof o ? o : {}, p = d.iterator || "@@iterator", v = d.asyncIterator || "@@asyncIterator", h = d.toStringTag || "@@toStringTag";
                function y(r, n, o) {
                    return Object.defineProperty(r, n, {
                        value: o,
                        enumerable: !0,
                        configurable: !0,
                        writable: !0
                    }),
                    r[n]
                }
                try {
                    y({}, "")
                } catch (r) {
                    y = function(r, n, o) {
                        return r[n] = o
                    }
                }
                function m(o, i, u, a) {
                    var c, s, l, d, p = Object.create((i && n(i.prototype, O) ? i : O).prototype);
                    return f(p, "_invoke", {
                        value: (c = o,
                        s = u,
                        l = new M(a || []),
                        d = b,
                        function(n, o) {
                            if (d === j)
                                throw Error("Generator is already running");
                            if (d === w) {
                                if ("throw" === n)
                                    throw o;
                                return {
                                    value: r,
                                    done: !0
                                }
                            }
                            for (l.method = n,
                            l.arg = o; ; ) {
                                var i = l.delegate;
                                if (i) {
                                    var u = function n(o, i) {
                                        var u = i.method
                                          , a = o.iterator[u];
                                        if (a === r)
                                            return i.delegate = null,
                                            "throw" === u && o.iterator.return && (i.method = "return",
                                            i.arg = r,
                                            n(o, i),
                                            "throw" === i.method) || "return" !== u && (i.method = "throw",
                                            i.arg = TypeError("The iterator does not provide a '" + u + "' method")),
                                            x;
                                        var c = g(a, o.iterator, i.arg);
                                        if ("throw" === c.type)
                                            return i.method = "throw",
                                            i.arg = c.arg,
                                            i.delegate = null,
                                            x;
                                        var s = c.arg;
                                        return s ? s.done ? (i[o.resultName] = s.value,
                                        i.next = o.nextLoc,
                                        "return" !== i.method && (i.method = "next",
                                        i.arg = r),
                                        i.delegate = null,
                                        x) : s : (i.method = "throw",
                                        i.arg = TypeError("iterator result is not an object"),
                                        i.delegate = null,
                                        x)
                                    }(i, l);
                                    if (u) {
                                        if (u === x)
                                            continue;
                                        return u
                                    }
                                }
                                if ("next" === l.method)
                                    l.sent = l._sent = l.arg;
                                else if ("throw" === l.method) {
                                    if (d === b)
                                        throw d = w,
                                        l.arg;
                                    l.dispatchException(l.arg)
                                } else
                                    "return" === l.method && l.abrupt("return", l.arg);
                                d = j;
                                var a = g(c, s, l);
                                if ("normal" === a.type) {
                                    if (d = l.done ? w : "suspendedYield",
                                    a.arg === x)
                                        continue;
                                    return {
                                        value: a.arg,
                                        done: l.done
                                    }
                                }
                                "throw" === a.type && (d = w,
                                l.method = "throw",
                                l.arg = a.arg)
                            }
                        }
                        )
                    }),
                    p
                }
                function g(r, n, o) {
                    try {
                        return {
                            type: "normal",
                            arg: r.call(n, o)
                        }
                    } catch (r) {
                        return {
                            type: "throw",
                            arg: r
                        }
                    }
                }
                i.wrap = m;
                var b = "suspendedStart"
                  , j = "executing"
                  , w = "completed"
                  , x = {};
                function O() {}
                function T() {}
                function k() {}
                var S = {};
                y(S, p, function() {
                    return this
                });
                var P = u && u(u(N([])));
                P && P !== s && l.call(P, p) && (S = P);
                var C = k.prototype = O.prototype = Object.create(S);
                function A(r) {
                    ["next", "throw", "return"].forEach(function(n) {
                        y(r, n, function(r) {
                            return this._invoke(n, r)
                        })
                    })
                }
                function I(r, n) {
                    var o;
                    f(this, "_invoke", {
                        value: function(i, u) {
                            function a() {
                                return new n(function(o, a) {
                                    (function o(i, u, a, c) {
                                        var s = g(r[i], r, u);
                                        if ("throw" !== s.type) {
                                            var f = s.arg
                                              , d = f.value;
                                            return d && "object" == _(d) && l.call(d, "__await") ? n.resolve(d.__await).then(function(r) {
                                                o("next", r, a, c)
                                            }, function(r) {
                                                o("throw", r, a, c)
                                            }) : n.resolve(d).then(function(r) {
                                                f.value = r,
                                                a(f)
                                            }, function(r) {
                                                return o("throw", r, a, c)
                                            })
                                        }
                                        c(s.arg)
                                    }
                                    )(i, u, o, a)
                                }
                                )
                            }
                            return o = o ? o.then(a, a) : a()
                        }
                    })
                }
                function R(r) {
                    var n = {
                        tryLoc: r[0]
                    };
                    1 in r && (n.catchLoc = r[1]),
                    2 in r && (n.finallyLoc = r[2],
                    n.afterLoc = r[3]),
                    this.tryEntries.push(n)
                }
                function L(r) {
                    var n = r.completion || {};
                    n.type = "normal",
                    delete n.arg,
                    r.completion = n
                }
                function M(r) {
                    this.tryEntries = [{
                        tryLoc: "root"
                    }],
                    r.forEach(R, this),
                    this.reset(!0)
                }
                function N(n) {
                    if (n || "" === n) {
                        var o = n[p];
                        if (o)
                            return o.call(n);
                        if ("function" == typeof n.next)
                            return n;
                        if (!isNaN(n.length)) {
                            var i = -1
                              , u = function o() {
                                for (; ++i < n.length; )
                                    if (l.call(n, i))
                                        return o.value = n[i],
                                        o.done = !1,
                                        o;
                                return o.value = r,
                                o.done = !0,
                                o
                            };
                            return u.next = u
                        }
                    }
                    throw TypeError(_(n) + " is not iterable")
                }
                return T.prototype = k,
                f(C, "constructor", {
                    value: k,
                    configurable: !0
                }),
                f(k, "constructor", {
                    value: T,
                    configurable: !0
                }),
                T.displayName = y(k, h, "GeneratorFunction"),
                i.isGeneratorFunction = function(r) {
                    var n = "function" == typeof r && r.constructor;
                    return !!n && (n === T || "GeneratorFunction" === (n.displayName || n.name))
                }
                ,
                i.mark = function(r) {
                    return Object.setPrototypeOf ? Object.setPrototypeOf(r, k) : (r.__proto__ = k,
                    y(r, h, "GeneratorFunction")),
                    r.prototype = Object.create(C),
                    r
                }
                ,
                i.awrap = function(r) {
                    return {
                        __await: r
                    }
                }
                ,
                A(I.prototype),
                y(I.prototype, v, function() {
                    return this
                }),
                i.AsyncIterator = I,
                i.async = function(r, n, o, u, c) {
                    void 0 === c && (c = a);
                    var s = new I(m(r, n, o, u),c);
                    return i.isGeneratorFunction(n) ? s : s.next().then(function(r) {
                        return r.done ? r.value : s.next()
                    })
                }
                ,
                A(C),
                y(C, h, "Generator"),
                y(C, p, function() {
                    return this
                }),
                y(C, "toString", function() {
                    return "[object Generator]"
                }),
                i.keys = function(r) {
                    var n = Object(r)
                      , o = [];
                    for (var i in n)
                        o.push(i);
                    return o.reverse(),
                    function r() {
                        for (; o.length; ) {
                            var i = o.pop();
                            if (i in n)
                                return r.value = i,
                                r.done = !1,
                                r
                        }
                        return r.done = !0,
                        r
                    }
                }
                ,
                i.values = N,
                M.prototype = {
                    constructor: M,
                    reset: function(n) {
                        if (this.prev = 0,
                        this.next = 0,
                        this.sent = this._sent = r,
                        this.done = !1,
                        this.delegate = null,
                        this.method = "next",
                        this.arg = r,
                        this.tryEntries.forEach(L),
                        !n)
                            for (var o in this)
                                "t" === o.charAt(0) && l.call(this, o) && !isNaN(+c(o).call(o, 1)) && (this[o] = r)
                    },
                    stop: function() {
                        this.done = !0;
                        var r = this.tryEntries[0].completion;
                        if ("throw" === r.type)
                            throw r.arg;
                        return this.rval
                    },
                    dispatchException: function(n) {
                        if (this.done)
                            throw n;
                        var o = this;
                        function i(i, u) {
                            return c.type = "throw",
                            c.arg = n,
                            o.next = i,
                            u && (o.method = "next",
                            o.arg = r),
                            !!u
                        }
                        for (var u = this.tryEntries.length - 1; u >= 0; --u) {
                            var a = this.tryEntries[u]
                              , c = a.completion;
                            if ("root" === a.tryLoc)
                                return i("end");
                            if (a.tryLoc <= this.prev) {
                                var s = l.call(a, "catchLoc")
                                  , f = l.call(a, "finallyLoc");
                                if (s && f) {
                                    if (this.prev < a.catchLoc)
                                        return i(a.catchLoc, !0);
                                    if (this.prev < a.finallyLoc)
                                        return i(a.finallyLoc)
                                } else if (s) {
                                    if (this.prev < a.catchLoc)
                                        return i(a.catchLoc, !0)
                                } else {
                                    if (!f)
                                        throw Error("try statement without catch or finally");
                                    if (this.prev < a.finallyLoc)
                                        return i(a.finallyLoc)
                                }
                            }
                        }
                    },
                    abrupt: function(r, n) {
                        for (var o = this.tryEntries.length - 1; o >= 0; --o) {
                            var i = this.tryEntries[o];
                            if (i.tryLoc <= this.prev && l.call(i, "finallyLoc") && this.prev < i.finallyLoc) {
                                var u = i;
                                break
                            }
                        }
                        u && ("break" === r || "continue" === r) && u.tryLoc <= n && n <= u.finallyLoc && (u = null);
                        var a = u ? u.completion : {};
                        return a.type = r,
                        a.arg = n,
                        u ? (this.method = "next",
                        this.next = u.finallyLoc,
                        x) : this.complete(a)
                    },
                    complete: function(r, n) {
                        if ("throw" === r.type)
                            throw r.arg;
                        return "break" === r.type || "continue" === r.type ? this.next = r.arg : "return" === r.type ? (this.rval = this.arg = r.arg,
                        this.method = "return",
                        this.next = "end") : "normal" === r.type && n && (this.next = n),
                        x
                    },
                    finish: function(r) {
                        for (var n = this.tryEntries.length - 1; n >= 0; --n) {
                            var o = this.tryEntries[n];
                            if (o.finallyLoc === r)
                                return this.complete(o.completion, o.afterLoc),
                                L(o),
                                x
                        }
                    },
                    catch: function(r) {
                        for (var n = this.tryEntries.length - 1; n >= 0; --n) {
                            var o = this.tryEntries[n];
                            if (o.tryLoc === r) {
                                var i = o.completion;
                                if ("throw" === i.type) {
                                    var u = i.arg;
                                    L(o)
                                }
                                return u
                            }
                        }
                        throw Error("illegal catch attempt")
                    },
                    delegateYield: function(n, o, i) {
                        return this.delegate = {
                            iterator: N(n),
                            resultName: o,
                            nextLoc: i
                        },
                        "next" === this.method && (this.arg = r),
                        x
                    }
                },
                i
            }
            function O(r, n, o, i, u, c, s) {
                try {
                    var l = r[c](s)
                      , f = l.value
                } catch (r) {
                    return void o(r)
                }
                l.done ? n(f) : a.resolve(f).then(i, u)
            }
            function T(r) {
                return function() {
                    var n = this
                      , o = arguments;
                    return new a(function(i, u) {
                        var a = r.apply(n, o);
                        function c(r) {
                            O(a, i, u, c, s, "next", r)
                        }
                        function s(r) {
                            O(a, i, u, c, s, "throw", r)
                        }
                        c(void 0)
                    }
                    )
                }
            }
            function k(r, n) {
                var o = s(r);
                if (l) {
                    var i = l(r);
                    n && (i = f(i).call(i, function(n) {
                        return d(r, n).enumerable
                    })),
                    o.push.apply(o, i)
                }
                return o
            }
            function S(r) {
                for (var n = 1; n < arguments.length; n++) {
                    var o = null != arguments[n] ? arguments[n] : {};
                    n % 2 ? k(Object(o), !0).forEach(function(n) {
                        R(r, n, o[n])
                    }) : p ? Object.defineProperties(r, p(o)) : k(Object(o)).forEach(function(n) {
                        Object.defineProperty(r, n, d(o, n))
                    })
                }
                return r
            }
            function P(r, n) {
                for (var o = 0; o < n.length; o++) {
                    var i = n[o];
                    i.enumerable = i.enumerable || !1,
                    i.configurable = !0,
                    "value"in i && (i.writable = !0),
                    Object.defineProperty(r, L(i.key), i)
                }
            }
            function C() {
                try {
                    var r = !Boolean.prototype.valueOf.call(v(Boolean, [], function() {}))
                } catch (r) {}
                return (C = function() {
                    return !!r
                }
                )()
            }
            function A(r) {
                return (A = Object.setPrototypeOf ? u.bind() : function(r) {
                    return r.__proto__ || u(r)
                }
                )(r)
            }
            function I(r, n) {
                return (I = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(r, n) {
                    return r.__proto__ = n,
                    r
                }
                )(r, n)
            }
            function R(r, n, o) {
                return (n = L(n))in r ? Object.defineProperty(r, n, {
                    value: o,
                    enumerable: !0,
                    configurable: !0,
                    writable: !0
                }) : r[n] = o,
                r
            }
            function L(r) {
                var n = function(r, n) {
                    if ("object" != _(r) || !r)
                        return r;
                    var o = r[h];
                    if (void 0 !== o) {
                        var i = o.call(r, n || "default");
                        if ("object" != _(i))
                            return i;
                        throw TypeError("@@toPrimitive must return a primitive value.")
                    }
                    return ("string" === n ? String : Number)(r)
                }(r, "string");
                return "symbol" == _(n) ? n : n + ""
            }
            r.Sender = function(r) {
                var o, i, u, c;
                function s(r, o) {
                    var i, u, a;
                    return function(r, o) {
                        if (!n(r, o))
                            throw TypeError("Cannot call a class as a function")
                    }(this, s),
                    R((u = A(u = s),
                    i = function(r, n) {
                        if (n && ("object" == _(n) || "function" == typeof n))
                            return n;
                        if (void 0 !== n)
                            throw TypeError("Derived constructors may only return object or undefined");
                        return function(r) {
                            if (void 0 === r)
                                throw ReferenceError("this hasn't been initialised - super() hasn't been called");
                            return r
                        }(r)
                    }(this, C() ? v(u, [], A(this).constructor) : u.apply(this, a))), "config", {}),
                    R(i, "client", {}),
                    i.client = r,
                    i.config = S({}, o),
                    i.updateConfig(o),
                    i.info("sender 初始化"),
                    i
                }
                return function(r, n) {
                    if ("function" != typeof n && null !== n)
                        throw TypeError("Super expression must either be null or a function");
                    r.prototype = Object.create(n && n.prototype, {
                        constructor: {
                            value: r,
                            writable: !0,
                            configurable: !0
                        }
                    }),
                    Object.defineProperty(r, "prototype", {
                        writable: !1
                    }),
                    n && I(r, n)
                }(s, r),
                o = [{
                    key: "init",
                    value: function() {}
                }, {
                    key: "send",
                    value: function(r) {
                        try {
                            this.emit(x.LifecycleEvent.beforeSend, r),
                            this.doSend(r)
                        } catch (r) {
                            (0,
                            b.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "doSend",
                    value: function(r) {
                        try {
                            this.emit(x.LifecycleEvent.send, r),
                            this.sendXHR(r)
                        } catch (r) {
                            (0,
                            b.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "sendXHR",
                    value: (u = T(E().mark(function r(n, o, i) {
                        var u, a, c, s, l, f;
                        return E().wrap(function(r) {
                            for (; ; )
                                switch (r.prev = r.next) {
                                case 0:
                                    if (a = this.client.config.config,
                                    c = (null === (u = n.data) || void 0 === u || null === (u = u.events) || void 0 === u || null === (u = u[0]) || void 0 === u ? void 0 : u.eventType) === x.ReportEventType.customEvent ? null == a ? void 0 : a.reportCustomUrl : null == a ? void 0 : a.reportUrl) {
                                        r.next = 5;
                                        break
                                    }
                                    return this.error("上报接口地址为空"),
                                    r.abrupt("return");
                                case 5:
                                    s = [];
                                    try {
                                        var d, p;
                                        null != n && null !== (l = n.data) && void 0 !== l && y(d = l.events).call(d, function(r) {
                                            return "e" === r.eventType
                                        }) && (n.data.events = null == n || null === (f = n.data) || void 0 === f ? void 0 : m(p = f.events).call(p, function(r) {
                                            var n;
                                            return null != r && null !== (n = r.ext) && void 0 !== n && n.elmNode && (s.push(r.ext.elmNode),
                                            delete r.ext.elmNode),
                                            r
                                        }))
                                    } catch (r) {
                                        (0,
                                        b.asyncThrowError)(r)
                                    }
                                    return r.prev = 7,
                                    r.next = 10,
                                    (0,
                                    j.postJSON)(c, {
                                        body: n
                                    });
                                case 10:
                                    this.info("发送成功"),
                                    null != s && s.length && (null == s || s.forEach(function(r) {
                                        try {
                                            r.getAttribute("data-tlg-exposured-v3") || r.setAttribute("data-tlg-exposured-v3", !0)
                                        } catch (r) {
                                            (0,
                                            b.asyncThrowError)(r)
                                        }
                                    })),
                                    null == i || i(o || []),
                                    r.next = 20;
                                    break;
                                case 15:
                                    r.prev = 15,
                                    r.t0 = r.catch(7),
                                    this.error("发送失败，开始重发", r.t0),
                                    this.retryRequest(c, n, o || [], "xhr", 3, 1e3),
                                    (0,
                                    b.asyncThrowError)(r.t0);
                                case 20:
                                case "end":
                                    return r.stop()
                                }
                        }, r, this, [[7, 15]])
                    })),
                    function(r, n, o) {
                        return u.apply(this, arguments)
                    }
                    )
                }, {
                    key: "updateConfig",
                    value: function(r) {
                        try {
                            this.config = S(S({}, this.config), r)
                        } catch (r) {
                            (0,
                            b.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "retryRequest",
                    value: (c = T(E().mark(function r(n, o, i, u, c, s) {
                        var l, f, d, p;
                        return E().wrap(function(r) {
                            for (; ; )
                                switch (r.prev = r.next) {
                                case 0:
                                    return r.prev = 0,
                                    this.info("尝试重发 次数:", c),
                                    p = null,
                                    r.next = 5,
                                    (0,
                                    j.postJSON)(n, {
                                        body: o
                                    });
                                case 5:
                                    (p = r.sent) && ("string" != typeof (null === (l = p) || void 0 === l ? void 0 : l.body) || null !== (f = JSON.parse((null === (d = p) || void 0 === d ? void 0 : d.body) || {})) && void 0 !== f && f.flag) || this.error("Request failed"),
                                    r.next = 19;
                                    break;
                                case 9:
                                    if (r.prev = 9,
                                    r.t0 = r.catch(0),
                                    !(c > 1)) {
                                        r.next = 18;
                                        break
                                    }
                                    return r.next = 14,
                                    new a(function(r) {
                                        return setTimeout(r, s)
                                    }
                                    );
                                case 14:
                                    return r.next = 16,
                                    this.retryRequest(n, o, i, u, c - 1, s + 1e3);
                                case 16:
                                    r.next = 19;
                                    break;
                                case 18:
                                    (0,
                                    b.asyncThrowError)(r.t0);
                                case 19:
                                case "end":
                                    return r.stop()
                                }
                        }, r, this, [[0, 9]])
                    })),
                    function(r, n, o, i, u, a) {
                        return c.apply(this, arguments)
                    }
                    )
                }, {
                    key: "destroy",
                    value: function() {}
                }, {
                    key: "info",
                    value: function() {
                        for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                            i[u] = arguments[u];
                        return (n = this.client.logs).info.apply(n, g(r = ["sender"]).call(r, i))
                    }
                }, {
                    key: "error",
                    value: function() {
                        for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                            i[u] = arguments[u];
                        return (n = this.client.logs).error.apply(n, g(r = ["sender"]).call(r, i))
                    }
                }],
                P(s.prototype, o),
                i && P(s, i),
                Object.defineProperty(s, "prototype", {
                    writable: !1
                }),
                s
            }(w.EventEmitter)
        }
    })
      , oj = u({
        "src/client/index.ts": function(r) {
            var o = tw()
              , i = tO()
              , u = tS()
              , a = tC()
              , c = tM()
              , s = tB()
              , l = tH()
              , f = tX()
              , d = t2()
              , p = tG()
              , v = tZ();
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            r.Client = void 0;
            var h = rW()
              , y = k(np())
              , m = n7()
              , g = n9()
              , b = or()
              , j = ob()
              , w = nK()
              , x = nI()
              , _ = nd()
              , E = oe()
              , O = k(nR())
              , T = k(nf());
            function k(r) {
                return r && r.__esModule ? r : {
                    default: r
                }
            }
            function S(r) {
                return (S = "function" == typeof o && "symbol" == typeof i ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof o && r.constructor === o && r !== o.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            function P(r, n) {
                var o = u(r);
                if (a) {
                    var i = a(r);
                    n && (i = c(i).call(i, function(n) {
                        return s(r, n).enumerable
                    })),
                    o.push.apply(o, i)
                }
                return o
            }
            function C(r) {
                for (var n = 1; n < arguments.length; n++) {
                    var o = null != arguments[n] ? arguments[n] : {};
                    n % 2 ? P(Object(o), !0).forEach(function(n) {
                        M(r, n, o[n])
                    }) : l ? Object.defineProperties(r, l(o)) : P(Object(o)).forEach(function(n) {
                        Object.defineProperty(r, n, s(o, n))
                    })
                }
                return r
            }
            function A(r, n) {
                for (var o = 0; o < n.length; o++) {
                    var i = n[o];
                    i.enumerable = i.enumerable || !1,
                    i.configurable = !0,
                    "value"in i && (i.writable = !0),
                    Object.defineProperty(r, N(i.key), i)
                }
            }
            function I() {
                try {
                    var r = !Boolean.prototype.valueOf.call(f(Boolean, [], function() {}))
                } catch (r) {}
                return (I = function() {
                    return !!r
                }
                )()
            }
            function R(r) {
                return (R = Object.setPrototypeOf ? d.bind() : function(r) {
                    return r.__proto__ || d(r)
                }
                )(r)
            }
            function L(r, n) {
                return (L = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(r, n) {
                    return r.__proto__ = n,
                    r
                }
                )(r, n)
            }
            function M(r, n, o) {
                return (n = N(n))in r ? Object.defineProperty(r, n, {
                    value: o,
                    enumerable: !0,
                    configurable: !0,
                    writable: !0
                }) : r[n] = o,
                r
            }
            function N(r) {
                var n = function(r, n) {
                    if ("object" != S(r) || !r)
                        return r;
                    var o = r[p];
                    if (void 0 !== o) {
                        var i = o.call(r, n || "default");
                        if ("object" != S(i))
                            return i;
                        throw TypeError("@@toPrimitive must return a primitive value.")
                    }
                    return ("string" === n ? String : Number)(r)
                }(r, "string");
                return "symbol" == S(n) ? n : n + ""
            }
            r.Client = function(r) {
                var o, i;
                function u(r) {
                    var o, i, a;
                    return function(r, o) {
                        if (!n(r, o))
                            throw TypeError("Cannot call a class as a function")
                    }(this, u),
                    M((i = R(i = u),
                    o = function(r, n) {
                        if (n && ("object" == S(n) || "function" == typeof n))
                            return n;
                        if (void 0 !== n)
                            throw TypeError("Derived constructors may only return object or undefined");
                        return function(r) {
                            if (void 0 === r)
                                throw ReferenceError("this hasn't been initialised - super() hasn't been called");
                            return r
                        }(r)
                    }(this, I() ? f(i, [], R(this).constructor) : i.apply(this, a))), "config", {}),
                    M(o, "bridgeTrackP", !1),
                    M(o, "initTrackP", !1),
                    M(o, "collects", []),
                    M(o, "configManager", {}),
                    M(o, "builder", null),
                    M(o, "started", !1),
                    M(o, "inited", !1),
                    M(o, "preStartQueue", []),
                    M(o, "getPgRef", function(r) {
                        try {
                            return (0,
                            E.getPageReferByInfo)(o.config, r)
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                        return null
                    }),
                    M(o, "getPgRefByElem", function(r) {
                        try {
                            if (!r)
                                return null;
                            var n = o.baseNode.xpath(r)
                              , i = n.scm
                              , u = n.elemId;
                            return o.getPgRef({
                                elemId: u || "",
                                cid: i.cid,
                                ctype: i.ctype,
                                traceId: i.traceId
                            })
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                        return null
                    }),
                    M(o, "getScmByElem", function(r) {
                        try {
                            if (!r)
                                return null;
                            var n = o.baseNode.xpath(r).scm;
                            return {
                                cid: n.cid,
                                ctype: n.ctype,
                                traceId: n.traceId
                            }
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                        return null
                    }),
                    M(o, "getJumpUrlByPgRef", function(r, n) {
                        try {
                            if (!r)
                                return null;
                            var i = r
                              , u = o.getPgRef(n);
                            if (-1 !== i.indexOf("pgRef="))
                                i = i.replace(/pgRef=[^&]+/, "pgRef=".concat(u));
                            else {
                                var a, c, s = -1 !== i.indexOf("?") ? "&" : "?";
                                i = v(a = v(c = "".concat(i)).call(c, s, "pgRef=")).call(a, u)
                            }
                            return i
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                        return null
                    }),
                    M(o, "pageHashReload", function() {
                        clearTimeout(o.routerChangeTimer),
                        o.routerChangeTimer = setTimeout(function() {
                            try {
                                var r = o.config.allowHash;
                                !(0,
                                _.hasHashNode)() && r && o.pageRouterReload()
                            } catch (r) {
                                (0,
                                _.asyncThrowError)(r)
                            }
                        }, 500)
                    }),
                    M(o, "pageRouterReload", function() {
                        clearTimeout(o.routerChangeTimer),
                        o.routerChangeTimer = setTimeout(function() {
                            try {
                                o.destroy(),
                                o.init(C(C({}, o.config), window.tlg))
                            } catch (r) {
                                (0,
                                _.asyncThrowError)(r)
                            }
                        }, 500)
                    }),
                    M(o, "resetTlog", function() {
                        try {
                            o.destroy(),
                            o.init(C(C({}, o.config), window.tlg))
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                    }),
                    M(o, "track", function(r) {
                        try {
                            var n = (0,
                            _.setEventSeq)()
                              , i = {
                                ev_type: x.EventTypes[r.type],
                                payload: C(C({}, r), {}, {
                                    eventSeq: n
                                })
                            };
                            o.report(i)
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                    }),
                    M(o, "tracke", function() {
                        var r = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : {}
                          , n = o.getCollectItem("exposure");
                        null == n || n.tracke(r)
                    }),
                    M(o, "exposure", function(r) {
                        var n = o.getCollectItem("exposure");
                        null == n || n.exposure(r || window.tlg)
                    }),
                    M(o, "trackc", function(r, n) {
                        if (r) {
                            var i = o.getCollectItem("click");
                            null == i || i.trackc(r, n)
                        } else
                            o.error("未传入事件对象")
                    }),
                    M(o, "tracks", function(r) {
                        var n = o.getCollectItem("showDailog");
                        null == n || n.tracks(r)
                    }),
                    M(o, "tracka", function(r) {
                        var n = o.getCollectItem("alive");
                        null == n || n.tracka(r)
                    }),
                    M(o, "trackp", function(r) {
                        var n = o.getCollectItem("pageView");
                        null == n || n.trackp(r)
                    }),
                    M(o, "trackCustomEvent", function() {
                        var r = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : {}
                          , n = (0,
                        _.setEventSeq)();
                        o.report({
                            ev_type: x.ReportEventType.customEvent,
                            payload: {
                                type: x.ReportEventType.customEvent,
                                eventId: null == r ? void 0 : r.eventId,
                                eventSeq: n,
                                ext: C(C({}, null == r ? void 0 : r.dataInfo), null == r ? void 0 : r.ext)
                            }
                        })
                    }),
                    M(o, "sendPgRefToApp", function(r) {
                        try {
                            void 0 !== window.XWebView && (null === h.callNativePromise || void 0 === h.callNativePromise || (0,
                            h.callNativePromise)({
                                plugin: "APPTlog",
                                action: "postMessage",
                                params: {
                                    pgRef: r
                                }
                            }))
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                    }),
                    M(o, "push", function() {}),
                    o.config = C(C({}, y.default), r),
                    o.userConfig = o.config,
                    o.started = !1,
                    o.sender = null,
                    o.preStartQueue = [],
                    o.logs = new w.Log,
                    o.bridgeTrackP = !1,
                    o.initTrackP = !1,
                    o.baseNode = new O.default,
                    o.lastSendTime = (0,
                    _.now)(),
                    o.routerChangeTimer = null,
                    o
                }
                return function(r, n) {
                    if ("function" != typeof n && null !== n)
                        throw TypeError("Super expression must either be null or a function");
                    r.prototype = Object.create(n && n.prototype, {
                        constructor: {
                            value: r,
                            writable: !0,
                            configurable: !0
                        }
                    }),
                    Object.defineProperty(r, "prototype", {
                        writable: !1
                    }),
                    n && L(r, n)
                }(u, r),
                o = [{
                    key: "init",
                    value: function(r) {
                        var n = this;
                        this.started || this.inited || (this.inited = !0,
                        (0,
                        _.tlogReady)(function() {
                            n.emit(x.LifecycleEvent.init, n),
                            n.config = C(C({}, n.config), r),
                            n.userConfig = n.config,
                            n.start(),
                            n.initModules()
                        }))
                    }
                }, {
                    key: "start",
                    value: function() {
                        try {
                            this.emit(x.LifecycleEvent.start, this),
                            this.initConfigManager(),
                            this.handleBridge(),
                            this.routerListener()
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "initModules",
                    value: function() {
                        try {
                            this.initBuilder(),
                            this.initSender(),
                            this.loadCollects()
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "loadCollects",
                    value: function() {
                        var r = this;
                        try {
                            (0,
                            m.getCollects)().forEach(function(n) {
                                return r.collects.push(n(r, r.config))
                            })
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "initConfigManager",
                    value: function() {
                        var r = this;
                        try {
                            this.emit(x.LifecycleEvent.beforeConfig, this.config, this),
                            this.configManager = new g.ConfigManager(this,this.config,this.userConfig),
                            this.configManager.on(x.LifecycleEvent.config, function(n) {
                                r.emit(x.LifecycleEvent.config, n)
                            }),
                            this.configManager.onReady(function() {
                                r.handlePreStartQueue()
                            })
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "initBuilder",
                    value: function() {
                        var r = this;
                        try {
                            this.builder = new b.Builder(this,this.config),
                            this.builder.on(x.LifecycleEvent.beforeBuild, function(n) {
                                r.emit(x.LifecycleEvent.beforeBuild, n)
                            }),
                            this.builder.on(x.LifecycleEvent.build, function(n) {
                                r.emit(x.LifecycleEvent.build, n)
                            })
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "initSender",
                    value: function() {
                        var r = this;
                        try {
                            this.sender = new j.Sender(this,this.config),
                            this.sender.on(x.LifecycleEvent.beforeSend, function(n) {
                                r.emit(x.LifecycleEvent.beforeSend, n)
                            }),
                            this.sender.on(x.LifecycleEvent.send, function(n) {
                                r.emit(x.LifecycleEvent.send, n)
                            })
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "info",
                    value: function() {
                        for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                            i[u] = arguments[u];
                        return (n = this.logs).info.apply(n, v(r = ["client"]).call(r, i))
                    }
                }, {
                    key: "error",
                    value: function() {
                        for (var r, n, o = arguments.length, i = Array(o), u = 0; u < o; u++)
                            i[u] = arguments[u];
                        return (n = this.logs).error.apply(n, v(r = ["client"]).call(r, i))
                    }
                }, {
                    key: "send",
                    value: function(r) {
                        var n;
                        this.lastSendTime = (0,
                        _.now)(),
                        null === (n = this.sender) || void 0 === n || n.send(r)
                    }
                }, {
                    key: "report",
                    value: function(r) {
                        this.emit(x.LifecycleEvent.report, r);
                        try {
                            if (this.started) {
                                var n, o = this.config.ignoreAction;
                                if (null != o && o.length && (-1 !== o.indexOf(r.ev_type) || -1 !== o.indexOf("*")))
                                    return;
                                var i = (0,
                                _.generateSessionId)()
                                  , u = this.configManager.getConfig({
                                    obj: i
                                });
                                this.builder.report(r, u)
                            } else
                                this.info("未完成配置初始化, 缓存数据", r),
                                this.preStartQueue.length < ((null === (n = this.configManager) || void 0 === n || null === (n = n.config) || void 0 === n ? void 0 : n.preStartQueueMaxCount) || 100) || this.preStartQueue.shift(),
                                this.preStartQueue.push(r)
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "updateConfig",
                    value: function(r, n) {
                        try {
                            this.config = C(C({}, this.config), r),
                            this.userConfig = C(C({}, this.userConfig), n),
                            this.updateModulesConfig(this.config)
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "updateModulesConfig",
                    value: function(r) {
                        try {
                            var n, o, i, u, a, c;
                            null === (n = this.configManager) || void 0 === n || null === (o = n.updateConfig) || void 0 === o || o.call(n, r),
                            null === (i = this.sender) || void 0 === i || null === (u = i.updateConfig) || void 0 === u || u.call(i, r),
                            null === (a = this.builder) || void 0 === a || null === (c = a.updateConfig) || void 0 === c || c.call(a, r)
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "destroy",
                    value: function() {
                        try {
                            var r;
                            this.inited = !1,
                            this.started = !1,
                            this.bridgeTrackP = !1,
                            this.initTrackP = !1,
                            this.collects && this.collects.forEach(function(r) {
                                var n;
                                null == r || null === (n = r.destroy) || void 0 === n || n.call(r)
                            }),
                            this.preStartQueue = [],
                            null === (r = this.sender) || void 0 === r || r.destroy(),
                            this.config = C({}, y.default),
                            this.userConfig = this.config,
                            (0,
                            _.removeEventListener)(window, "hashchange", this.pageHashReload),
                            (0,
                            _.removeEventListener)(window, "popstate", this.pageRouterReload),
                            (0,
                            _.removeEventListener)(window, "pushState", this.pageRouterReload),
                            (0,
                            _.removeEventListener)(window, "replaceState", this.pageRouterReload)
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "handlePreStartQueue",
                    value: function() {
                        var r = this;
                        try {
                            this.started = !0,
                            this.preStartQueue.forEach(function(n) {
                                r.report(n)
                            }),
                            this.preStartQueue = []
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "routerListener",
                    value: function() {
                        try {
                            if (!this.config.spa)
                                return;
                            history.pushState = (0,
                            _.dispatch)("pushState"),
                            history.replaceState = (0,
                            _.dispatch)("replaceState"),
                            (0,
                            _.addEventListener)(window, "hashchange", this.pageHashReload),
                            (0,
                            _.addEventListener)(window, "popstate", this.pageRouterReload),
                            (0,
                            _.addEventListener)(window, "pushState", this.pageRouterReload),
                            (0,
                            _.addEventListener)(window, "replaceState", this.pageRouterReload)
                        } catch (r) {
                            (0,
                            _.asyncThrowError)(r)
                        }
                    }
                }, {
                    key: "getCollectItem",
                    value: function(r) {
                        var n;
                        return null === (n = this.collects) || void 0 === n ? void 0 : c(n).call(n, function(n) {
                            return (null == n ? void 0 : n.type) === r
                        })[0]
                    }
                }, {
                    key: "handleBridge",
                    value: function() {
                        var r = this;
                        !this.initTrackP && (0,
                        _.checkLiepinApp)() && T.default.registerHandler("bridgeAppToH5", function(n) {
                            var o = null;
                            try {
                                o = JSON.parse(n),
                                r.initTrackP || parseInt(o.type, 10) || (r.bridgeTrackP = !0,
                                r.trackp())
                            } catch (r) {
                                (0,
                                _.asyncThrowError)(r)
                            }
                        })
                    }
                }],
                A(u.prototype, o),
                i && A(u, i),
                Object.defineProperty(u, "prototype", {
                    writable: !1
                }),
                u
            }(w.EventEmitter)
        }
    })
      , ow = u({
        "src/index.ts": function(r) {
            var n = tw()
              , o = tO()
              , i = tS()
              , u = tC()
              , a = tM()
              , c = tB()
              , s = tH()
              , l = tG()
              , f = tX()
              , d = tZ();
            function p(r) {
                return (p = "function" == typeof n && "symbol" == typeof o ? function(r) {
                    return typeof r
                }
                : function(r) {
                    return r && "function" == typeof n && r.constructor === n && r !== n.prototype ? "symbol" : typeof r
                }
                )(r)
            }
            Object.defineProperty(r, "__esModule", {
                value: !0
            }),
            Object.defineProperty(r, "LifecycleEvent", {
                enumerable: !0,
                get: function() {
                    return h.LifecycleEvent
                }
            }),
            r.createClient = j,
            r.default = void 0;
            var v = oj()
              , h = nK()
              , y = nd();
            function m(r, n) {
                var o = i(r);
                if (u) {
                    var s = u(r);
                    n && (s = a(s).call(s, function(n) {
                        return c(r, n).enumerable
                    })),
                    o.push.apply(o, s)
                }
                return o
            }
            function g(r, n) {
                return (g = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(r, n) {
                    return r.__proto__ = n,
                    r
                }
                )(r, n)
            }
            function b() {
                try {
                    var r = !Boolean.prototype.valueOf.call(f(Boolean, [], function() {}))
                } catch (r) {}
                return (b = function() {
                    return !!r
                }
                )()
            }
            function j() {
                for (var r, n = arguments.length, o = Array(n), i = 0; i < n; i++)
                    o[i] = arguments[i];
                if (window.tlog)
                    return null === (r = window.tlog) || void 0 === r || r.updateConfig.apply(r, d(o).call(o, o)),
                    window.tlog;
                var u = function(r, n, o) {
                    if (b())
                        return f.apply(null, arguments);
                    var i = [null];
                    i.push.apply(i, n);
                    var u = new (r.bind.apply(r, i));
                    return o && g(u, o.prototype),
                    u
                }(v.Client, o);
                return window.tlog || (window.tlog = u),
                u
            }
            nf(),
            (0,
            y.generateUuid)(),
            r.default = function() {
                for (var r, n = arguments.length, o = Array(n), i = 0; i < n; i++)
                    o[i] = arguments[i];
                if (window.tlog)
                    return null === (r = window.tlog) || void 0 === r || r.updateConfig.apply(r, d(o).call(o, o)),
                    window.tlog;
                var u = j.apply(void 0, o);
                return u.init.apply(u, o),
                u
            }(function(r) {
                for (var n = 1; n < arguments.length; n++) {
                    var o = null != arguments[n] ? arguments[n] : {};
                    n % 2 ? m(Object(o), !0).forEach(function(n) {
                        (function(r, n, o) {
                            var i;
                            (i = function(r, n) {
                                if ("object" != p(r) || !r)
                                    return r;
                                var o = r[l];
                                if (void 0 !== o) {
                                    var i = o.call(r, n || "default");
                                    if ("object" != p(i))
                                        return i;
                                    throw TypeError("@@toPrimitive must return a primitive value.")
                                }
                                return ("string" === n ? String : Number)(r)
                            }(n, "string"),
                            (n = "symbol" == p(i) ? i : i + "")in r) ? Object.defineProperty(r, n, {
                                value: o,
                                enumerable: !0,
                                configurable: !0,
                                writable: !0
                            }) : r[n] = o
                        }
                        )(r, n, o[n])
                    }) : s ? Object.defineProperties(r, s(o)) : m(Object(o)).forEach(function(n) {
                        Object.defineProperty(r, n, c(o, n))
                    })
                }
                return r
            }({}, window.tlg || {}))
        }
    })()
}
,
"object" == typeof module && "object" == typeof module.exports ? t(exports) : "function" == typeof define && define.amd ? define(["exports"], t) : (e = "undefined" != typeof globalThis ? globalThis : e || self) && t(e.index = {});
