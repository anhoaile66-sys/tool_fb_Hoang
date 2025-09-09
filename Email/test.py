import uiautomator2 as u2
import time

a="""<p style="text-align: justify;"><strong style="font-size: 14px; text-align: justify;">CV xin việc</strong><span style="font-size:14px;"> là một yếu tố đầu tiên quan trọng, có giá trị quyết định tới quá trình tìm kiếm việc làm của chúng ta. Ở những bài viết trước, chúng ta đã nắm cơ bản về </span>
<style type="text/css"><!--td {border: 1px solid #ccc;}br {mso-data-placement:same-cell;}-->
</style>
<span style="font-size:14px;"><strong><a href="https://timviec365.vn/cv365/cv-viet-tat-cua-tu-gi-nhung-dieu-can-biet-khi-viet-cv.html" target="_blank">cv xin việc là gì</a></strong> hay một bản CV viết chuẩn và cách điền sơ yếu lý lịch chuyên nghiệp là như thế nào, Trong đó, đầu mục kinh nghiệm việc làm nắm giữ phần lớn sự thành công của mỗi người, đồng thời, nó cũng là tâm điểm mà mỗi nhà tuyển dụng chú ý để đánh giá ứng viên. Nhưng có một nghịch lý vô cùng bất lợi cho đối tượng đi xin việc là sinh viên mới ra trường đó là họ hoàn toàn chưa có kinh nghiệm việc làm. Có chăng chỉ là những kinh nghiệm nhỏ nhặt, chớp nhoáng của thời sinh viên với việc học hành là chính. Thế nên không thể tránh khỏi việc thiếu kinh nghiệm việc làm? Chẳng lẽ vì như thế mà những bạn sinh viên mới ra trường chấp nhận sự thất bại phủ đầu này hay sao? Đừng lo, chỉ cần các bạn tìm ra lời đáp cho câu hỏi "<em><strong>Viết gì vào CV nếu bạn thiếu kinh nghiệm làm việc"?</strong></em> thì đã có thể gây ấn tượng bằng một cách khác.</span></p>
<p style="text-align: justify;"><span style="font-size:14px;">Dưới đây chính là những bí quyết hiệu quả nhất giúp bạn có tạo CV xin việc ấn tượng và thu hút nhà tuyển dụng nhất kể cả khi thiếu kinh nghiệm.</span></p>
<p style="text-align: center;"><img alt="Cách viết CV chuẩn cho người thiếu kinh nghiệm" height="903" src="/cv365/upload/images/cv-cho-nguoi-thieu-kinh-nghiem-lam-viec-1.jpg" width="638"/></p>
<p style="text-align: justify;"><span style="font-size:14px;">Bạn là sinh viên mới ra trường và bạn chưa biết cách viết CV ấn tượng để lọt vào mắt xanh nhà tuyển dụng. Vậy hãy để Timviec365 hướng dẫn bạn cách viết CV ấn tượng dành riêng cho người chưa có kinh nghiệm khi <strong><a href="https://timviec365.vn/tim-viec-lam.html" target="_blank"><span style="color:#FF0000;">tìm việc làm</span></a></strong> ngay nhé.</span></p>
<p style="text-align: justify;"><span style="font-size:14px;">Để tạo một CV ấn tượng với nhà tuyển dụng thì bạn cần phải làm nổi bật ưu điểm của mình và hiểu được vị trí bạn đang ứng tuyển tại công ty, bạn hãy tận dụng điểm mạnh đó một cách triệt để nhất. CV xin việc cũng tương tự như một sơ yếu lý lịch mẫu có giá trị quan trọng quyết định đến buổi phỏng vấn của bạn nên hãy thực sự tập trung và đầu tư để có bộ hồ sơ xin việc ấn tượng nhất. Bạn có thể tự thiết kế một CV cho riêng bản thân mình hoặc sử dụng </span><span style="font-size:14px;"><a href="https://timviec365.vn/cv365/mau-cv-xin-viec-online" target="_blank"><strong><span style="color:#FF0000;">mẫu CV xin việc</span></strong></a> để hoàn thiện ngay.</span></p>
<h2 style="text-align: justify;"><span style="font-size:16px;"><strong>1. Nội dung không thể thiếu trong 1 CV</strong></span></h2>
<p style="text-align: justify;"><span style="font-size:14px;"><strong>Thông tin cá nhân</strong>: Họ và tên, ngày/tháng/năm/sinh, giới tính, email, địa chỉ liên hệ, số điện thoại.</span></p>
<p style="text-align: justify;"><span style="font-size:14px;"><strong>Trình độ học vấn</strong> của bạn: Chuyên ngành bạn theo học, năm tốt nghiệp, những khóa ngắn hạn có liên quan. Các thành tích nổi bật, có thể kèm bằng khen (nếu có).</span></p>
<p style="text-align: justify;"><span style="font-size:14px;"><strong>Kinh nghiệm làm việc</strong>: Bạn nên sắp xếp theo thứ tự từ công việc đã làm trước kia đến công việc gần đây nhất. Nhấn mạnh vị trí bạn đảm nhiệm và thành tựu bạn đạt được.</span></p>
<p style="text-align: justify;"><span style="font-size:14px;">Nếu bạn là sinh viên mới ra trường chưa hề có kinh nghiệm, thì tại mục này các bạn nên liệt kê một số thành tích tại trường, những hoạt động ngoại khóa và một số kĩ năng bạn đã học được trong quá trình đi làm thêm.</span></p>
<p style="text-align: justify;"><strong><span style="font-size:14px;">Một số kỹ năng được nhà tuyển dụng quan tâm</span></strong></p>
<p style="text-align: center;"><em><span style="font-size:14px;"><img alt="Kỹ năng cần có trong CV cho người thiếu kinh nghiệm" height="400" src="/cv365/upload/images/cv-cho-nguoi-thieu-kinh-nghiem-lam-viec-2.jpg" width="640"/></span></em></p>
<p style="text-align: justify;"><span style="font-size: 14px;">Dù bạn ứng tuyển ở vị trí hay công việc nào thì những <strong><a href="https://timviec365.vn/blog/cac-ky-nang-trong-cv-new3541.html" target="_blank">kỹ năng trong CV xin việc</a></strong> được nhà tuyển dụng rất quan tâm như:</span></p>
<ul>
<li style="text-align: justify;"><span style="font-size:14px;">Các kỹ năng giải quyết vấn đề</span></li>
<li style="text-align: justify;"><span style="font-size:14px;">Các kỹ năng giao tiếp và kỹ năng thuyết trình</span></li>
<li style="text-align: justify;"><span style="font-size:14px;">Kỹ năng về quản lý thời gian</span></li>
<li style="text-align: justify;"><span style="font-size:14px;">Kỹ năng làm việc nhóm</span></li>
<li style="text-align: justify;"><span style="font-size:14px;">Ngôn ngữ: Trình bày về ngôn ngữ cần sử dụng súc tích, tránh sự dài dòng.</span></li>
<li style="text-align: justify;"><span style="font-size:14px;">Sở thích: Thể hiện được cá tính của bạn nhưng không quá phô trương.</span></li>
</ul>
<h2 style="text-align: justify;"><span style="font-size:16px;"><strong>2. Viết CV xin việc với sự mở đầu thật ấn tượng</strong></span></h2>
<p style="text-align: justify;"><span style="font-size:14px;">Sử dụng một câu văn hay một đoạn văn tóm tắt ngắn gọn nhưng thật sự ấn tượng.  Đây là một điều mà bất cứ người tuyển dụng nào cũng chú ý trước tiên cho nên quan trọng nhất là việc bạn nên làm đúng cách. Những bí quyết hàng đầu đó chính là phải trình bày một cách thật sự ngắn gọn và thật sự đơn giản. Không cần quá dài dòng như cần sự súc tích, cô đọng. Để <strong><a href="https://timviec365.vn/cv365/cach-viet-phan-mo-dau-cv-xin-viec-an-tuong-va-thu-hut-nhat.html" target="_blank">phần mở đầu CV xin việc</a> </strong>ấn tượng thì bạn nên bắt đầu với những thông tin về mặt trình độ , học vấn, kỹ năng tiêu biểu nhất. Những điều này đương nhiên sẽ có nhiều diện tích hơn nữa để trình bày cụ thể hơn ở mục sau nên ở phần mở đầu này chỉ cần tóm tắt để làm nổi bật nhất về mặt chuyên môn mà bạn đã theo học cùng với những thành tích tốt nghiệp đã đạt được nếu như bạn cảm thất rằng nó có thể đáp ứng thật tốt vai trò mà nhà tuyển dụng có thể tìm kiếm. Đồng thời những thông tin này cũng có thể giúp bạn tạo ra những ấn tượng tích cực cho CV xin việc của mình.</span></p>
<p style="text-align: justify;"><span style="font-size:14px;">Thế nên bạn hãy hiểu thật rõ những sự kỳ vọng của mình. Nếu như chỉ mong muốn có thể dự tuyển được đúng vị trí cho một chuyên môn nhất định mà bạn mạnh thì bạn có thể nêu tóm tắt như thế này chẳng hạn: Tôi đang tìm công việc ...Còn nếu như muốn mở ra nhiều cơ hội hơn nữa cho bản thân mình để lựa chọn thì bạn cũng có thể nói một cách chung chung: Tôi đang tìm một vị trí việc làm có thể mang tới nhiều thử thách, giúp tôi vận dụng nhiều khả năng,....</span></p>
<p style="text-align: center;"><span style="font-size:14px;"><img alt="Cách viết CV có mở đầu ấn tượng cho người thiếu kinh nghiệm" height="533" src="/cv365/upload/images/cv-cho-nguoi-thieu-kinh-nghiem-lam-viec-3.png" width="800"/></span></p>
<h2 style="text-align: justify;"><span style="font-size:16px;"><strong>3. Đề cao yếu tố trung thực trong CV xin việc</strong></span></h2>
<p style="text-align: justify;"><span style="font-size:14px;">Hiện nay, chúng ta có thể giới thiệu sơ qua về bản thân thông qua CV hay <strong>COVER LETTER MẪU</strong> khá phổ biến trên mạng. Tuy nhiên làm thế nào để ghi điểm trong mắt nhà tuyển dụng từ khi đọc hồ sơ của bạn? Cái nền tảng về tính cách con người bạn sẽ được các nhà tuyển dụng tinh ý nhìn ra ngay từ cách bạn khai báo thông tin cá nhân <strong>ho so ly lich</strong> của mình. Tất cả mọi người đều sẽ có phần này trong sơ yếu lý lịch, nhưng cách thực hiện của chúng ta là khác nhau. Một bản Profile đầy đủ, chỉ tiết sẽ chứng minh rằng con người bạn rất cẩn thận, bao quát và trách nhiệm với chính bản thân mình. Nhà tuyển dụng cần đức tính tốt đẹp đó và nó cần thiết cho tất cả mọi lĩnh vực ngành nghề.</span></p>
<p style="text-align: justify;"><span style="font-size:14px;">Trong sự chi tiết, tỉ mỉ này, bạn hãy chú ý liệt kê ra ra những kỹ năng nổi bật. Nhớ là đề cao tính chất nổi bật nhé. Nếu quá lan man dài dòng với cả những thứ không cần thiết, có thể nhà tuyển dụng mới chỉ kịp chú ý tới chúng mà vô tình bỏ qua thế mạnh bạn đã note vào.</span></p>
<h2 style="text-align: justify;"><span style="font-size:16px;">4. <strong>Có mục tiêu nghề nghiệp rõ ràng</strong></span></h2>
<p style="text-align: justify;"><span style="font-size:14px;">Chấp nhận rằng bạn – một sinh viên mới ra trường không có kinh nghiệm việc làm. Âu đó cũng là quy luật hết sức tự nhiện. Nhưng không vì thế mà bạn để mình bị cuốn vào sự thất bại vô lý rằng không có kinh nghiệm việc làm sẽ thất bại 50%. Dường như ai cũng sẽ phải trải qua giai đoạn này, bởi ai cũng sẽ một lần đứng trong vai trò của một tân cử nhân mới ra trường, trong tay chỉ có tấm bằng tốt nghiệp và tri thức “cày cuốc” được suốt những năm tháng miệt mài ngồi trên ghế nhà trường mà không có kinh nghiệm việc làm.</span></p>
<p style="text-align: justify;"><span style="font-size:14px;">Trong trường hợp này, vui lòng thay thế kinh nghiệm bằng một hướng dẫn, một <strong><a href="https://timviec365.vn/cv365/nhung-luu-y-khi-viet-muc-tieu-nghe-nghiep-trong-cv-de-toa-sang.html" target="_blank">mục tiêu nghề nghiệp trong CV</a></strong> rõ ràng. Bởi việc này sẽ thể hiện được bạn là người luôn luôn sẵn sàng chờ đón một cơ hội nào đó. Bạn nên đưa vào trong bản CV từ 1 đến 2 câu nói về những điểm mạnh, những lợi thế sở thích và nguyện vọng, liên kết chúng với nghề nghiệp bạn hướng tới. Chắc chắn rằng, khi đọc được bản CV như vậy, nhà tuyển dụng sẽ thấy được sự mới mẻ trong con người của bạn. Họ sẽ đánh giá cao về tinh thần, sự nhiệt huyết và tâm thế sẵn sàng cho những kế hoạch, chiến lược mới của bạn.</span></p>
<p style="text-align: center;"><span style="font-size:14px;"><img alt="Mục tiêu nghề nghiệp trong CV cho người thiếu kinh nghiệm" height="415" src="/cv365/upload/images/cv-cho-nguoi-thieu-kinh-nghiem-lam-viec-4.png" width="800"/></span></p>
<h2 style="text-align: justify;"><span style="font-size:16px;"><strong>5. Tập trung trình bày về kỹ năng thay vì kể lể về vai trò</strong></span></h2>
<p style="text-align: justify;"><span style="font-size:14px;">CV xin việc làm hầu như đều được bắt đầu bằng cách liệt kê lại các tên công ty mà ứng viên đã rời đi gần đây nhất. Tuy nhiên đối với bạn, với những người sinh viên mới ra trường thì những kinh nghiệm và bề dày đó chưa hề có do họ chưa đi làm ở đâu ngoài việc đến trường học tập mỗi ngày. Hoặc cũng có thể là bạn chỉ làm việc ở một nơi mà có ngành nghề không mấy liên quan tới chuyên môn thì tốt nhất là bạn nên viết trong bản CV xin việc của mình những kỹ năng là thế mạnh của bạn.  </span></p>
<p style="text-align: justify;"><span style="font-size:14px;">Thêm những kỹ năng của bản thân vào CV sẽ giúp bạn có thêm điểm cộng trong mắt những nhà tuyển dụng, khi làm việc tại vị trí nào đó luôn phải cần một vài kỹ năng để thực hiện công việc được hiệu quả nhất như kỹ năng giao tiếp, làm việc theo nhóm, thuyết trình trước đáng đông, sử dụng thành thạo các phần mềm tin học văn phòng,…</span></p>
<p style="text-align: justify;"><span style="font-size:14px;">Khi bạn có được kỹ năng sẵn có khác cùng với những hỗ trợ kèm theo sẽ giúp bạn làm việc được tốt hơn. Những kỹ năng của bạn có liên quan đến vị trí cần tuyển hoặc không liên quan cũng là một yêu cầu quan trọng của nhà tuyển dụng khi <strong>tìm việc làm ở Phường Phương Liên - Hà Nội</strong>. Trong số nhiều <strong><a href="https://timviec365.vn/cv365/cv-cho-nguoi-chua-co-kinh-nghiem.html" target="_blank">CV xin việc cho người chưa có kinh nghiệm</a></strong> mà bạn có thêm những kỹ năng vào đó sẽ vừa giúp công việc của mình hiệu quả hơn mà còn hỗ trợ những bộ phận khác được tốt hơn.</span></p>
<p style="text-align: justify;"><span style="font-size:14px;">Vì vậy mà đây chính là lúc để chúng ta vận dụng những danh sách các kỹ năng của mình cùng với những ví dụ cụ thể. Để có thể mô tả công việc hiệu quả thì bạn nên nhanh chóng tham khảo cũng như kết hợp một số các trải nghiệm khác biệt lại cùng với nhau. Thông qua những bằng chứng hết sức cụ thể phục vụ hữu dụng nhất cho việc xác thực, cách thể hiện và trình bày này của các bạn cũng sẽ giúp cho bản CV xin việc làm có thể gây được ấn tượng vô cùng mạnh mẽ.</span></p>
<h2 style="text-align: justify;"><span style="font-size:16px;"><strong>6. Làm rõ những vấn đề về bằng cấp</strong></span></h2>
<p style="text-align: justify;"><span style="font-size:14px;">Nếu tạo một bản CV xin việc làm quá đơn điệu chỉ vì lý do thiếu kinh nghiệm thì đó quả là một điều gì đó sai lầm. Vậy nên thay vào đó thì bạn hãy làm đẹp nó nhờ những yếu tố khác trong đó có bằng cấp. Đó là một cách tuyệt vời để có thể giúp bạn chứng minh về năng lực của bạn. Nếu như bạn đã từng viết luận án thì bạn có thể nói nhiều hơn về khả năng tìm kiếm của mình, cùng với đó là khả năng tổng hợp, xử lý thông tin. Nếu như bạn thường xuyên thực hiện nhiệm vụ thuyết trình  thì chẳng còn gì tuyệt vời hơn việc nhấn mạnh về kỹ năng trình bày vấn đề và khả năng thuyết phục. Ngoài ra có thể nhăc tới các khả năng như làm việc một cách độc lập tốt ở trong dự án, lên kế hoạch, tổ chức kế hoạch và phối hợp với những người đồng đội của mình ở trong những sự kiện.</span></p>
<p style="text-align: center;"><span style="font-size:14px;"><img alt="Trình bày bằng cấp trong CV cho người thiếu kinh nghiệm" height="391" src="/cv365/upload/images/cv-cho-nguoi-thieu-kinh-nghiem-lam-viec-5.png" width="800"/></span></p>
<p style="text-align: justify;"><span style="font-size:14px;">Ngoài ra, bạn cũng không nên bỏ quên những bằng cấp khác đã nhận được sự chứng thực. Ví dụ như bằng lái xe hơi, chứng nhận đã tham gia vào một khóa đào tạo nào đó vè lập trình, về Digital, về thiết kế , tuyển dụng,... Hãy thật mạnh dạn nêu a nếu như chúng có liên quan. Chỉ trừ việc nói dối về khả năng nào đó khi mà bạn thực sự không hề có nó.</span></p>
<h2 style="text-align: justify;"><span style="font-size:16px;"><strong>7.  Những kinh nghiệm có được từ hoạt động ngoại khóa</strong></span></h2>
<p style="text-align: justify;"><span style="font-size:14px;">Nếu như nhà tuyển dụng đòi hỏi cao về kinh nghiệm, đừng quá lo lắng về điều đó khi bạn mới ra trường. Bởi dù họ có mong muốn điều đó thực sự nhưng họ sẽ chẳng bao giờ đánh đồng những yêu cầu khắt khe ấy quy chụp mọi trường hợp. Vẫn sẽ có những cơ hội dành riêng cho “lính mới”, vấn đề của bạn là làm mình nổi bật nhất trong số tất cả các lính mới đang cùng hướng đến một vị trí việc làm. Chúng ta nên nhớ rằng, kinh nghiệm việc làm không nhất thiết được đến từ công việc cụ thể nào đó tại một công ty nào đó, mà nó đến từ những hoạt động, việc làm hàng ngày đã được đúc rút thành kinh nghiệm, có liên quan trực tiếp đến vị trí việc làm chúng ta đang muốn ứng tuyển.</span></p>
<p style="text-align: justify;"><span style="font-size:14px;">Do vậy, hãy đúc kết mọi kinh nghiệm đến từ các hoạt động ngoại khóa trong suốt quá trình học tập của bạn. Như chúng ta đã từng tham gia vào các tổ chức, câu lạc bộ,... hay các công việc thực tập, <strong>việc làm Partime</strong>, <strong>viec lam buoi toi</strong>... cũng sẽ mang tới những trải nghiệm đầu đời để sau khi ra trường bạn có thể bắt đầu với công việc một cách suôn sẻ nhất. Hãy đưa chúng vào mục kinh nghiệm việc làm. Nó sẽ là một yếu tố quan trọng giúp bạn trúng tuyển.</span></p>
<p style="text-align: justify;"><span style="font-size:14px;">Đừng ngần ngại đưa nó vào trong bản <strong><a href="https://timviec365.vn/cv365/cach-viet-cv-cho-sinh-vien-moi-ra-truong-dep-chuan-nhat.html" target="_blank">CV xin việc cho sinh viên mới ra trường</a></strong> của mình hoặc khi thực hiện <strong>cách ghi hồ sơ xin việc làm</strong>. Vì ai cũng biết, con người được tôi luyện như thế nào chính nhờ tới việc tham gia vào các hội nhóm đó. Và đương nhiên nhà tuyển dụng sẽ hiểu được bạn đã được rèn luyện các kỹ năng nhất định, phù hợp với công việc như thế nào? Đồng thời, chúng ta cũng sẽ ghi được dấu ấn tốt bởi những lời đánh giá linh hoạt, năng động, nhiệt tình từ phía nhà tuyển dụng. Chẳng có lý do gì để bạn không lọt vào mắt xanh của nhà tuyển dụng, vượt qua hàng chục đối thủ có cùng xuất phát điểm “thiếu” kinh nghiệm việc làm giống như bạn.</span></p>
<h2 style="text-align: justify;"><span style="font-size:16px;"><strong>8.  Kinh nghiệm đến từ những trải nghiệm học tập</strong></span></h2>
<p style="text-align: justify;"><span style="font-size:14px;">Ngoài kinh nghiệm đi làm thực tế ra, nhà tuyển dụng còn chú trọng tới kỹ năng, kiến thức liên quan đến công việc. Vì thế, đây còn là điểm giúp bạn “gỡ” lại việc thiếu kinh nghiệm việc làm. Để tìm được việc làm tốt khi mới ra trường thì ngay thời điểm còn ngồi trên ghế nhà trường, các bạn cần phải phấn đấu hết mình để đạt được những thành tích học tập xuất sắc.</span></p>
<p style="text-align: justify;"><span style="font-size:14px;">Cũng nên tham gia những khóa học có liên quan mật thiết đến công việc mà tương lai chúng ta sẽ theo đuổi. Mặc dù chúng ta chưa có cơ hội làm việc để tích lũy kinh nghiệm thực tiễn,  nhưng bản thân chúng ta đã có một quá trình học tpaaj, trau dồi vững chắc những bước đi quan trọng, cần thiết cho tương lai. Đó chính là điểm cộng mà nhà tuyển dụng hết sức ưng ý ở bạn với nét đẹp là sự chủ động, sự cố gắng  để phát triển bản thân không ngừng. Và đương nhiên, chẳng có lý do gì để họ từ chối một ứng cử viên sáng giá như vậy.</span></p>
<p style="text-align: center;"><span style="font-size:14px;"><img alt="Trình bày kinh nghiệm học tập trên CV cho người thiếu kinh nghiệm" height="400" src="/cv365/upload/images/cv-cho-nguoi-thieu-kinh-nghiem-lam-viec-6.jpg" width="650"/></span></p>
<h2 style="text-align: justify;"><span style="font-size:16px;"><strong>9. Thêm giải thưởng, giấy chứng nhận nào bạn có khi tìm việc đi làm ngay tại Hà Nội</strong></span></h2>
<p style="text-align: justify;"><span style="font-size:14px;">Thực tế những hồ sơ xin việc hay những sơ yếu lý lịch đi làm ngay thông thường không phải ai cũng có nhiều kinh nghiệm lâu năm, việc bạn không có nhiều kinh nghiệm cũng không phải là điều quá tồi tệ. Vì vậy bạn có thể bù vào kinh nghiệm thay bằng những điểm nổi bật của bản thân so với những người cùng trang lứa như thành tích học tập chuyên môn, giải thưởng ở những hoạt động bạn tham gia trong trường.</span></p>
<p style="text-align: justify;"><span style="font-size:14px;">Nếu là sinh viên mới ra trường thì nhà tuyển dụng <strong>việc đi làm ngay tại Hà Nội</strong> chủ yếu muốn xem thái độ khi làm việc, tư chất của bản thân vì vậy bạn có thể thể hiện những điểm nổi bật của bản thân cho nhà tuyển dụng <strong>việc đi làm ngay tại Hà Nội</strong> như khả năng thuyết trình, làm việc cộng đồng, tham gia hội hiến máu của trường, hoặc thậm chí có thể nói về 1 vài sở trưởng có thể giúp ích cho mình.</span></p>
<blockquote>
<p style="text-align: justify;"><em style="font-size: 14px; text-align: justify;"><strong>Bạn nên đọc: </strong></em><a href="https://timviec365.vn/cv365/cach-thiet-ke-cv-xin-viec-tren-microsoft-moi-va-chuyen-nghiep-nhat.html" style="font-size: 14px; text-align: justify;" target="_blank"><span style="color: rgb(0, 0, 255);"><em><strong>Cách thiết kế CV xin việc trên Microsoft mới và chuyên nghiệp nhất</strong></em></span></a></p>
</blockquote>
<h2 style="text-align: justify;"><span style="font-size:16px;"><strong>10. Cần thêm một chút sự cá tính</strong></span></h2>
<p style="text-align: justify;"><span style="font-size:14px;">Bạn nên xem bản thân mình có mối quan tâm thú vị nào đặc biệt hay không? Chẳng hạn như từng đạt giải thưởng hay là tham gia vào cuộc đua lớn nào đó, hay là một tay lặn cừ khôi, leo núi, nhảy dù,... Những điều này nên được viết vào bản CV xin việc. Nhà tuyển dụng vốn dĩ nhận được nhiều bộ hồ sơ tham gia dự tuyển với những phong cách giống nhau, chỉ cần có một người khác biệt đối với cả đám đông thì có thể sẽ gây ra sự tò mò  và được nhà tuyển dụng ghi nhớ nhiều hơn. Nếu như không có được khả năng gặt hái thành tích trong quá khứ thì chớ cố làm quá lên. Bạn chỉ cần liệt kê đơn giản những sở thích của bản thân vào trong mục thông tin thêm. Bởi vì chúng có thể gợi nhắc thêm về tính cách của bạn.</span></p>
<p style="text-align: justify;"><strong><span style="font-size:14px;">Cuối cùng, hãy hoàn chỉnh CV của mình</span></strong></p>
<p style="text-align: center;"><img alt="Hoàn chỉnh cv tìm việc cho người chưa có kinh nghiệm" height="450" src="/cv365/upload/images/CV-mau(1).jpg" width="600"/></p>
<p style="text-align: justify;"><span style="font-size:14px;">Sự hoàn chỉnh ở đây không chỉ đánh giá từ mặt đầy đủ mà còn đòi hỏi tính logic. Cái khó nằm ở đó, nhưng nếu bạn vượt qua được sự khó khăn này thì thực sự nhà tuyển dụng sẽ đánh giá rất cao trí tuệ của bạn. Hãy coi bản CV trong <strong>hồ sơ mẫu xin việc</strong> đó chứa đựng câu chuyện mà bạn thực lòng muốn kể cho người tuyển dụng nghe. Nếu chỉ đơn giản là những gạch đầu dòng thật khô cứng thì đương nhiên người nghe sẽ cảm thấy thật sự tẻ nhạt, không có gì thú vị. Sức hấp dẫn sẽ phụ thuộc vào tài năng bạn kể chuyện, nhẹ nhàng thôi nhưng sâu sắc và lắng đọng.</span></p>
<p style="text-align: justify;"><span style="font-size:14px;">Trên đây là những <strong><a href="https://timviec365.vn/cv365/cach-viet-cv-xin-viec-an-tuong-nhat-trong-mat-cac-nha-tuyen-dung.html" target="_blank">cách viết CV xin việc</a></strong> cực kỳ hiệu quả cho những bạn chưa có kinh nghiệm, bạn hoàn toàn có thể xin được công việc như mong muốn nếu biết cách làm nổi bật những </span>
<style type="text/css"><!--td {border: 1px solid #ccc;}br {mso-data-placement:same-cell;}-->
</style>
<span style="font-size:14px;"><strong><a href="https://timviec365.vn/cv365/diem-manh-diem-yeu-cua-ban-la-gi-cach-viet-diem-manh-trong-cv.html" target="_blank">điểm mạnh của bản thân</a></strong> ghi trong CV. Bạn cũng có thể tìm kiếm những mẫu CV xin việc, <strong>mẫu thư xin việc</strong> sẵn có trên mạng để không bị mắc phải những sai lầm khi tạo hồ sơ. </span></p>
<p style="text-align: justify;"><span style="font-size:14px;">Chúc bạn nhanh chóng thành công trên con đường sự nghiệp đã định hướng.</span></p>
<blockquote>
<p style="text-align: justify;"><em style="font-size: 14px; text-align: justify;"><strong>Bạn nên đọc: </strong></em><a href="https://timviec365.vn/cv365/mot-mau-cv-xin-viec-lam-dung-chuan-la-nhu-the-nao-b73.html" target="_blank"><strong><em><span style="font-size:14px;"><span style="color:#0000FF;">Một mẫu CV xin việc làm đúng chuẩn là như thế nào?</span></span></em></strong></a></p>
</blockquote>
"""

def open_html_app(d):
    """
    Mở app HTML Editor trên thiết bị
    Lưu ý khi mở app phải ở trong thẻ .html rồi 
    sử dụng weditor để dễ bề biết trước xpath
    """
    d(resourceId="com.android.systemui:id/center_group").click()
    d.swipe_ext("up", scale=0.8)
    time.sleep(1)
    d(resourceId="com.gogo.launcher:id/search_container_all_apps").click()
    time.sleep(1)
    d.send_keys("Html Editor", clear=True)
    time.sleep(1)
    d.xpath('//*[@resource-id="com.gogo.launcher:id/branch_suggest_app_list_rv"]/android.view.ViewGroup[1]/android.widget.ImageView[1]').click()
    time.sleep(2)
    print("Đang mở app HTML Editor...")

def clear_old_html(d,width, height):
    # Lấy kích thước màn hình
    x = width * 0.325
    y = height * 0.323
    d.long_click(x, y, duration=1.0)
    time.sleep(1)
    if d(text="Select all").exists(timeout=3):
        d(text="Select all").click()
        time.sleep(0.5)
        d.press("del")
        print("Đã xoá cũ")
    else:
        print("Không tìm thấy tuỳ chọn Select all")
        # anh Cả quất tiếp nhé
    d.send_keys(a)

def compile_html(d):
    d(description="Run").click()
    time.sleep(2)
    (0.058, 0.193)
    x = width * 0.058
    y = height * 0.193
    d.long_click(x, y, duration=1.0)
    time.sleep(1)
    if d(text="Chọn tất cả").exists(timeout=3):
        d(text="Chọn tất cả").click()
        time.sleep(0.5)
        d(text="Sao chép").click()
    elif d(text="Select all").exists(timeout=3):
        d(text="Select all").click()
        time.sleep(0.5)
        d(text="Copy").click()
    else:
        print("Không tìm thấy tuỳ chọn Select all")

        
def go_back_code_html(d):
    d.xpath('//android.widget.ScrollView/android.view.View[1]/android.view.View[1]/android.view.View[1]/android.widget.TextView[1]').click()

        
# Kết nối với thiết bị
d = u2.connect()

# Lấy kích thước màn hình
width, height = d.window_size()

# # Tính toán tọa độ thực từ tỷ lệ
# x = width * 0.492
# y = height * 0.372

# # Kiểm tra và click vào tùy chọn "Dán"
# if d(text="Dán").exists(timeout=3):
#     d(text="Dán").click()
#     print("Đã dán thành công")
# else:
#     print("Không tìm thấy tùy chọn Dán")
#     # Nếu không tìm thấy, có thể thử chụp màn hình để debug
#     d.screenshot("debug.png")
    
open_html_app(d)
clear_old_html(d,width, height)
compile_html(d)
go_back_code_html(d)
