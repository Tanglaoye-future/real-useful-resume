# BOSS直聘加密算法分析报告

分析文件数: 5000

---


## SIGN_PATTERN (1167 处)


**文件**: `a30\b.java`

```java
gCode");         String str8 = (String) a2.c(map, "tab");         String str9 = (String) a2.c(map, "encryptFissionUserId");         String str10 = (String) a2.c(map, "topContentId");         String st
```


**文件**: `a30\b.java`

```java
tionRequest = new GetMomentFissionRelationRequest(new a());         getMomentFissionRelationRequest.encryptFissionUserId = str;         getMomentFissionRelationRequest.execute();     } }
```


**文件**: `a30\c.java`

```java
/ java.lang.Runnable         public void run() {             String str = (String) this.f1097b.get("encryptFormId");             String str2 = (String) this.f1097b.get(SocialConstants.PARAM_SOURCE);
```


**文件**: `a30\c.java`

```java
new JumpPostVideoParam();             jumpPostVideoParam.setEditVideo(true).setClickSource("0").setEncryptFormId(str).setSource(str2);             GetRouter.i0(this.f1098c, jumpPostVideoParam);       
```


**文件**: `a30\e.java`

```java
&& LText.notEmpty(str5)) {                 JobBean jobBean = new JobBean();                 jobBean.encryptJobId = str8;                 jobBean.jobId = str4;                 jobBean.jobName = str5;
```


**文件**: `a30\e.java`

```java
ID);         String str7 = (String) a2.c(map, "jobName");         String str8 = (String) a2.c(map, "encryptJobId");         String str9 = (String) a2.c(map, "publishExtraInfo");         boolean zEqual
```


**文件**: `a9\b.java`

```java
w a(file);         } catch (Throwable th2) {             th2.printStackTrace();             b("type_encryption", Log.getStackTraceString(th2));             return h.b(gVar);         }     }      publi
```


**文件**: `a90\a.java`

```java
) {             return 1;         }         if (chatSource.isTargetChatSource("normal_source_chat_design_work")) {             return 4;         }         if (chatSource.isTargetChatSource("normal_sou
```


**文件**: `a90\a.java`

```java
.buttonContent)) ? 1 : 7;         }         if (chatSource.isTargetChatSource("normal_source_chat_design_work")) {             return 4;         }         if (chatSource.isTargetChatSource("normal_sou
```


**文件**: `ah0\b.java`

```java
return key == this || this.f3904b == key;     }      /* JADX WARN: Incorrect return type in method signature: (Lah0/f$b;)TE; */     public final f.b b(f.b element) {         i.e(element, "element");
```


## API_PATTERN (2 处)


**文件**: `b4\d.java`

```java
te */     public void g() {         c4.c.b("VerifyStatusPoller", "runTask");         h4.a.c().d().a("/api/themis/client/sanction/instruction/polling").d().b(new b());     }      void e() {         if 
```


**文件**: `j4\d.java`

```java
PREFIX, "1.0");     }      private static String b(String str) {         int iIndexOf = str.indexOf("/api/");         return iIndexOf >= 0 ? str.substring(iIndexOf) : str;     }      private static vo
```


## URL_PATTERN (296 处)


**文件**: `ba\a.java`

```java
public static ApmConfigBean d(Map<String, String> map) throws Throwable {         b.a aVarA = b.a("https://apm-and.zhipin.com/api/zpApm/user/config/get.json", map);         Throwable th2 = aVarA.f5050
```


**文件**: `bp\j.java`

```java
r4 = geekRecruitDetailResponse2.shareUrl;         if (TextUtils.isEmpty(str4)) {             str4 = "http://www.zhipin.com";         }         ShareCommon.Builder builderCreate = ShareCommon.Builder.c
```


**文件**: `c1\c.java`

```java
b b(f1.a aVar, Context context, String str) throws Throwable {         return d(aVar, context, str, "https://mcgw.alipay.com/sdklog.do", true);     }      @Override // a1.e     public String e(f1.a aV
```


**文件**: `c1\d.java`

```java
p");         map.put("productVersion", "15.8.10");         a.b bVarB = z0.a.b(context, new a.C1324a("https://loggw-exsdk.alipay.com/loggw/logUpload.do", map, bArrA));         h1.e.h("mspl", "mdap got 
```


**文件**: `d50\b.java`

```java
serverHighlightListBean.endIndex = g("《隐私政策》", str)[1];         serverHighlightListBean.subUrl = "https://about.zhipin.com/agreement?id=personalinfopro";         ServerHighlightListBean serverHighligh
```


**文件**: `d50\b.java`

```java
serverHighlightListBean3.endIndex = g("《权限列表》", str)[1];         serverHighlightListBean3.subUrl = "https://about.zhipin.com/agreement?id=9b0a4710643b48b1bcd064b919dc7225";         ServerHighlightList
```


**文件**: `d50\b.java`

```java
verHighlightListBean4.endIndex = g("《人脸验证服务协议》", str)[1];         serverHighlightListBean4.subUrl = "https://about.zhipin.com/agreement?id=17b357e7f70341bcb3fc1ac73c05b376";         arrayList.add(serv
```


**文件**: `dx\b.java`

```java
ses6.dex */ public class b {     public static void a(Activity activity) {         new k0(activity, "https://m.zhipin.com/H5/html/faq/appearAddress.html").g();     } }
```


## BASE64_ENCODE (10 处)


**文件**: `c3\a.java`

```java
new String(Base64.decode(str, 2));     }      private static String e(String str) {         return Base64.encodeToString(str.getBytes(), 2);     }      public static a g(@NonNull String str) {        
```


**文件**: `f\j.java`

```java
(), this.f116041c, fVar.f116030d));         try {             stringBuffer.append(URLEncoder.encode(Base64.encodeToString(fVar.f116028b.getBytes(), 0), "UTF-8"));             Intent intent = new Inten
```


**文件**: `k0\b.java`

```java
2609b = "0123456789ABCDEF".toCharArray();      public static String a(byte[] bArr) {         return Base64.encodeToString(bArr, 3);     }      public static SecureRandom b() {         if (f122608a != 
```


**文件**: `l1\a.java`

```java
utStream.toByteArray(), 0, bArr, 4, byteArrayOutputStream.toByteArray().length);             return Base64.encodeToString(bArr, 8);         } catch (Exception unused) {             return "";         
```


**文件**: `l1\a.java`

```java
am.close();                     byteArrayInputStream.close();                     return new String(Base64.encode(byteArray, 2));                 }                 gZIPOutputStream.write(bArr, 0, i11)
```


**文件**: `ng0\a.java`

```java
if (bArrD0 != null) {                                                 String strEncodeToString = Base64.encodeToString(bArrD0, r22);                                                 JSONObject jSONObje
```


**文件**: `nr\i0.java`

```java
G, a(j11, i11));         String strValueOf = String.valueOf(jE);         String strEncodeToString = Base64.encodeToString(bArr, 2);         TLog.debug("ProcessPushMsgStore", "enqueue payload length= %
```


**文件**: `sf0\d.java`

```java
r02 = fileInputStream;             sf0.a.a(r02);             throw th;         }         return Base64.encodeToString(r02, 2);     }      public static File B(String str) {         if (d0(str)) {     
```


**文件**: `t1\h.java`

```java
gZIPOutputStream.write(str.getBytes(str2));         gZIPOutputStream.close();         return Base64.encodeToString(byteArrayOutputStream.toByteArray(), 1);     }      public static String b(String str
```


## BASE64_DECODE (14 处)


**文件**: `c3\a.java`

```java
961a = str;         j();     }      private static String c(String str) {         return new String(Base64.decode(str, 2));     }      private static String e(String str) {         return Base64.encod
```


**文件**: `cmbapi\CMBApiEntryActivity.java`

```java
f (i11 != 200) {                 CMBApiEntryActivity.this.f6239b.loadDataWithBaseURL("", new String(Base64.decode(f.c.f116026m, 0)), "text/html", "UTF-8", "");             }             CMBApiEntryAct
```


**文件**: `cmbapi\CMBApiEntryActivity.java`

```java
);             this.f6242e.b("网络连接已断开");             this.f6239b.loadDataWithBaseURL("", new String(Base64.decode(f.c.f116026m, 0)), "text/html", "UTF-8", "");             return;         }         k.
```


**文件**: `cmbapi\CMBWebview.java`

```java
his.f6257b)) {             this.f6259d.b("网络连接已断开");             loadDataWithBaseURL("", new String(Base64.decode(c.f116026m, 0)), "text/html", "UTF-8", "");             return;         }         k.b(
```


**文件**: `f2\e.java`

```java
r.substring(0, iIndexOf).endsWith(";base64")) {                     return new ByteArrayInputStream(Base64.decode(str.substring(iIndexOf + 1), 0));                 }                 throw new IllegalA
```


**文件**: `j9\h.java`

```java
String strA = m8.v.a(KeyFactory.getInstance("RSA").generatePublic(new X509EncodedKeySpec(Base64.decode(str, 0))), str2);             p.b(f121134a, ">>> " + strA);             return strA;         } ca
```


**文件**: `jg0\a.java`

```java
th());         if (!TextUtils.isEmpty(str)) {             com.zhipin.spherecamerakit.utils.b.f(str, Base64.decode(str2, 0));             JSONObject jSONObject = new JSONObject();             jSONObjec
```


**文件**: `ng0\a.java`

```java
if (this.f128786p != null) {                     try {                         byte[] bArrDecode = Base64.decode(new JSONObject(str2).optString("data"), 0);                         this.f128786p.write
```


**文件**: `nr\i0.java`

```java
@Nullable     private static byte[] b(@NonNull String str) {         try {             return Base64.decode(str, 2);         } catch (Throwable unused) {             return null;         }     }      
```


**文件**: `od\y.java`

```java
(str == null || LText.empty(str)) {             return null;         }         byte[] bArrDecode = Base64.decode(str, 0);         Inflater inflater = new Inflater();         inflater.setInput(bArrDeco
```


## RSA (2 处)


**文件**: `m8\v.java`

```java
byteArrayOutputStream = new ByteArrayOutputStream();             try {                 cipher = Cipher.getInstance("RSA/ECB/PKCS1Padding");                 cipher.init(1, publicKey);                 b
```


**文件**: `x0\d.java`

```java
ry {                     PublicKey publicKeyB = b("RSA", str2);                     Cipher cipher = Cipher.getInstance("RSA/ECB/PKCS1Padding");                     cipher.init(1, publicKeyB);         
```


## HMAC (1 处)


**文件**: `okio\ByteString.java`

```java
private ByteString hmac(String str, ByteString byteString) {         try {             Mac mac = Mac.getInstance(str);             mac.init(new SecretKeySpec(byteString.toByteArray(), str));          
```
