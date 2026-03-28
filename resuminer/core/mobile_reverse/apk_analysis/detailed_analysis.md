# BOSS 直聘 APK 深度分析报告


## 发现的字符串特征

### API (4468 个)

- `Lcom/amap/api/col/3sl/l2;`
- `+Lcom/amap/api/services/route/DrivePathV2$1;`
- `Lcom/amap/api/col/3sl/nd;`
- `9Landroidx/appcompat/widget/AppCompatTextHelper$Api24Impl;`
- `;Lcom/amap/api/services/route/RouteSearch$TruckRouteQuery$1;`
- `7Lcom/amap/api/services/busline/BusLineQuery$SearchType;`
- `7[Lcom/amap/api/maps/model/PolylineOptions$LineJoinType;`
- `Lcom/amap/api/col/3sl/v;`
- `Lcom/amap/api/col/3sl/d7$a;`
- `HLcom/amap/api/services/routepoisearch/RoutePOISearch$RoutePOISearchType;`
- `-Lcom/amap/api/maps/model/HeatMapLayerOptions;`
- `Lcom/amap/api/col/3sl/g9;`
- `Lcom/amap/api/col/3sl/q1;`
- `6Lcom/amap/api/maps/model/animation/TranslateAnimation;`
- `-Lcom/amap/api/services/busline/BusLineSearch;`
- `2Landroidx/core/view/DisplayCutoutCompat$Api28Impl;`
- `8Landroidx/core/location/LocationManagerCompat$Api24Impl;`
- `'Lcom/amap/api/maps/model/LatLngCreator;`
- `$Lcom/amap/api/maps/model/Marker$a$2;`
- `-Landroidx/appcompat/widget/Toolbar$Api33Impl;`

### CRYPTO (893 个)

- `RSA/ECB/PKCS1Padding`
- `onSignalStrengthsChanged`
- `WEBP_SIGNATURE_1`
- `plusAssign`
- `aesEncrypt`
- `(Landroid/telephony/CellSignalStrengthNr;`
- `3https://mclient.alipay.com/home/exterfaceAssign.htm`
- `SHA1PRNG`
- `getConversationId`
- `design_tab_text_size_2line`
- `signingInfo`
- `getSigningCertificateHistory`
- `mCancellationSignal`
- `setSystemBarsAppearance`
- `getUnreadConversation`
- `design_fab_shadow_mid_color`
- `$isSupportedFormatForSavingAttributes`
- `mDesignIds`
- ``%s/v4/resolve?account_id=%s&tag=%s&sign=%s&t=%d&sdk_ver=%s&os_type=%s&alt_server_ip=true&type=%s`
- `getSignature`

### NETWORK (110 个)

- `VLcom/alibaba/fastjson/support/retrofit/Retrofit2ConverterFactory$RequestBodyConverter;`
- `ALcom/alibaba/fastjson/support/retrofit/Retrofit2ConverterFactory;`
- `0Lorg/apache/http/client/params/HttpClientParams;`
- `Lretrofit2/Converter$Factory;`
- `Lretrofit2/Converter;`
- `/Lorg/apache/http/impl/client/DefaultHttpClient;`
- `Lretrofit2/Converter<`
- `WLcom/alibaba/fastjson/support/retrofit/Retrofit2ConverterFactory$ResponseBodyConverter;`
- `Lretrofit2/Retrofit;`
- `#Lorg/apache/http/client/HttpClient;`
- `*AndroidHttpClient created and never closed`
- `Lokhttp3/i0;`
- `Lokhttp3/d0;`
- `Lokhttp3/j0;`
- `:Lcom/bumptech/glide/integration/okhttp3/OkHttpGlideModule;`
- `2Lcom/tencent/liteav/base/http/HttpClientAndroid$h;`
- `,Lcom/bumptech/glide/integration/okhttp3/a$a;`
- `DLcom/kanzhun/zpsdksupport/utils/businessutils/http/ZpOkHttpCallBack<`
- `Lokhttp3/a0$a;`
- `Lokhttp3/f$a;`

### KEYS (356 个)

- `tokenField`
- `WEBP_SIGNATURE_1`
- `Corg.springframework.security.oauth2.common.DefaultOAuth2AccessToken`
- `updateLocalUmidToken`
- `,Cannot convert json to point. Next token is `
- `apdidTokenCache`
- `getSignature`
- `CODE_AMAP_SIGNATURE_ERROR`
- `_quickNextTokenComma`
- `KEY_TOKEN`
- `RW2_SIGNATURE`
- `NotIncludeSignatures`
- `0sendReq failed for dd app signature check failed`
- `token`
- `<[Landroid/support/v4/media/session/MediaSessionCompat$Token;`
- `val$token`
- `verifyToken`
- `syntax error, unexpect token `
- `setToken`
- `Lorg.springframework.security.oauth2.common.DefaultExpiringOAuth2RefreshToken`


## 逆向建议

1. 重点关注包含 'sign', 'api', 'token' 的类
2. 分析 Network/Http 相关的代码
3. 查找加密算法的实现位置
4. 使用 Frida hook 关键方法
