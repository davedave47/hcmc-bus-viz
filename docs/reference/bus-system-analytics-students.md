## Bus system analytics 

TIST report 2026 

1 

## Một tuyến bus (1) 

1. Thông số chung về tuyến: 

   - Thời điểm mở & kết thúc tuyến, số ngày trong tuần, số chuyến trong ngày, giờ bắt đầu và kết thúc, trạm đầu & cuối, thời gian toàn chuyến, ID xe (số xe, tài xế, công ty) 

2. Số chuyến bus trong từng ngày có đúng kế hoạch không? 

   - Đủ số lượng 

   - Khởi hành đúng giờ 

Biểu đồ multi-dimensional data 

Max Mean Min 

   - Bảng số xe chạy đúng đăng ký 

3. Thời điểm bus đến trạm 

Biểu đồ Box 

- Biểu diễn theo (1) thời điểm & (2) theo thời gian tính từ thời điểm khởi hành chuyến 

- • Chọn lựa thống kê theo: 

`o` Khoảng thời gian nào: [startday, stopday] 

   - Ngày nào trong tuần [Mon, Sun] 

   - Khoảng thời gian trong ngày [start-time, stop-time] (tính theo giờ 0-24) 

   - Khung giờ cao điểm: [6:30-8:00] & [16:30-18:30] (tuỳ định nghĩa) 

   - `o` Và khung giờ không cao điểm. 

- Thống kê trung bình thời điểm/ thời gian bus đến từng trạm dùng biểu đồ Box, biểu đồ multi-dimensional data 

TIST report 2026 

2 

## Một tuyến bus (2) 

## 4. Phát hiện bất thường 

   - Thời gian đến trạm lệch (lớn hơn) mức trung trình một khoảng ngưỡng T (được người dùng chọn): thường lý do là kẹt xe hay có sự cố 

   - Thời gian đến một trạm X của chuyến Y vào một khung giờ cao điểm S 

   - Phân tích độ trễ của chuyến bus Y đến từng trạm theo thời gian (tháng, quý, năm) 

5. Phân tích yếu tố “mưa” 

   - Thu thập dữ liệu về mưa trên địa bàn (Sài gòn) trong quá khứ 

   - (Dự báo mưa trên địa bàn trong tương lai) 

   - Thu thập số liệu các chuyến có yếu tố mưa trong quá khứ 

   - Giải quyết bài toán “Dự báo trong một chuyến bus” nhưng có yếu tố mưa 

6. Phân tích yếu tố “kẹt xe” 

   - Thu thập dữ liệu về ‘kẹt xe” trên địa bàn (Sài gòn) trong quá khứ 

   - (Dự báo “kẹt xe” trên địa bàn trong tương lai) 

   - Thu thập số liệu các chuyến có yếu tố “kẹt xe” trong quá khứ 

   - Giải quyết bài toán “Dự báo trong một chuyến bus” nhưng có yếu tố “kẹt xe” 

TIST report 2026 

3 

## Một tuyến bus (3) 

7. Bài toán dự báo trong một tuyến bus 

   - Dự báo thời gian đến từng trạm bus theo từng chuyến (khung thời gian) 

   - Chọn thời gian bắt đầu của một chuyến bus Y thì dự báo thời gian đến tất cả các trạm X 

   - Đề xuất giờ khởi hành cho một chuyến bus Y để đảm bảo giờ đến một trạm X (hay nhiều trạm X) trong một khung giờ nào đó 

   - Dự báo tốc độ bus, thời gian di chuyển trên từng đoạn đường 

## 8. Đóng mở cửa 

- Thời gian từng chuyến bus dừng ở từng trạm 

- Suy ra các trạm khai thác hiệu quả (không hay ít dừng) & không hiệu quả 

## 9. Phân tích tốc độ bus 

- Tính tốc độ bus trong có vượt ngưỡng cho phép trên từng đoạn đường (có dữ liệu quy định tốc độ cho trước) 

- Tính vận tốc bus trên từng đoạn đường, khoảng cách 2 trạm và toàn tuyến theo thời gian. 

TIST report 2026 

4 

## Nhiều tuyến bus 

## 1. Giải pháp hiển thị thông tin trên bản đồ số 

   - Hiển thị tất cả các tuyến, tuyến bus xanh (dùng khí ga, điện,…) 

   - Các bộ lọc: theo khu vực (phường, trung tâm, ngoại thành…), thời gian (khung giờ), công ty xe bus,… 

   - Biểu diễn sự phát triển của hệ thống bus theo thời gian 

   - Chỉ số tuyến bus trên một khu vực 500x500m, 1000x1000m,… (xem them thông tin từ Sở GTVT) 

2. 

- Dashboard hiển thị thông tin nhiều tuyến bus 

- Có 2 mục tiêu chính: (1) Thông tin chung đại diện cho tất cả các tuyến bus, (2) Đối sánh (so sánh thông số của tuyến bus này và một hay nhiều tuyến bus khác) 

- Thông số của một tuyến: thời điểm mở & kết thúc tuyến, số ngày trong tuần, số chuyến trong ngày, giờ bắt đầu và kết thúc, trạm đầu & cuối, thời gian toàn chuyến, ID xe (số xe, tài xế, công ty) 

- Dùng biểu đồ 2D, biểu đồ Box, biểu đồ multi-dimensional data 

## 3. Phân tích 

- Phân tích các bất thường về từng chuyến bus: ví dụ thời gian chuyến bus đến trạm chậm vì lý do gì (kẹt xe, mưa,…?) 

- Phân tích việc kết nối hệ thống bus để di chuyển từ điểm A đến điểm B tối đa K lần đổi tuyến bus 

- Phân tích thời gian kết nối từ tuyến bus Y1 sang tuyến bus Y2 tại trạm X trong ngày có vượt quá một ngưỡng thời gian đợi W không? 

TIST report 2026 

5 

## Phân tích kết nối bus & metro 

1. Xem các tuyến bus có kết nối nối đến các trạm metro 2. Kế hoạch cho các tuyến bus có kết nối metro: số chuyến trong ngày, giờ khởi hành 

3. Thống kê dữ liệu bus ghé trạm kết nối metro 

4. Phân tích thời gian chuyển tiếp từ trạm metro X1 đến trạm X2 của tuyến bus Y có vượt quá một ngưỡng thời gian đợi W 

- => Giải pháp khắc phục: tăng chuyến bus Y, thay đổi thời gian khởi hành tuyến bus Y,… 

- 5. Dự báo thời gian bài toán số 4 ở trên xảy ra vì thời gian tuyến bus Y đến trạm X2 trễ dần theo thời gian nhưng thời gian metro đến trạn X1 không thay đổi 

TIST report 2026 

6 

## Phân tích hệ thống bus theo thời gian thực (1) 

1. Tìm thời gian di chuyển của bus theo thời gian thực trên từng đoạn đường (hoặc giữa 2 trạm trên 1 tuyến bus) theo từng slot thời gian (tính theo giờ) 

2. Dự báo thời gian di chuyển của bus trên từng đoạn đường theo từng slot thời gian trong tương lai (1 tuần, 1 tháng, 12 tháng) 

3. Tìm đường theo thời gian di chuyển ngắn nhất dùng bus (không giới hạn số lần đổi tuyến) để đi chuyển từ trạm A đến trạm B 

4. Tìm đường theo thời gian di chuyển ngắn nhất dùng bus để đi chuyển từ trạm A đến trạm B với ràng buộc: 

   - a) Số lần đổi tuyến tối đa K b) Số tiền ít nhất khi biết tiền vé từng tuyến bus 

5. Giải pháp tính toán giải bài toán 4 ở trên khi tiếp nhận nhiều câu hỏi tìm đường (query) từ người sử dụng cùng lúc: tìm lời giải gần đúng với chi phí tính toán thấp nên chia làm 2 bước: 

   - i. Tiền xử lý (tính toán trước) dạng offline để có các giá trị trung giam 

   - ii. Tính toán (online) cho từng câu hỏi tìm đường (query) từ người sử dụng 

TIST report 2026 

7 

## Phân tích hệ thống bus theo thời gian thực (2) 

6. Phân tích các điểm bất thường 

   - Di chuyển giữa hai trạm bus vượt quá ngưỡng K lần chuyển đổi tuyến 

   - Thời gian di chuyển tối đa giữa giữa hai trạm bus vượt quá một ngưỡng thời gian T trong một khung giờ (xem xét các trường hợp kẹt xe, mưa,…) 

   - Thời gian di chuyển lâu nhất giữa hai trạm bus nào 

7. Đánh giá tác động thực tế đến giao thông của một sự kiện như công trình xây dựng (cầu, chung cư, trường học), điều tiết giao thông (biến báo, đèn giao thông, luật giao thông,…), mùa (năm học, mùa hè),  lễ hội (các lễ hội, khai trường (tăng cư dân),…) 

   - Phân tích ảnh hưởng đến các thông số của từng tuyến bus để xem những tuyến nào ảnh hưởng và ảnh hưởng như thế nào giữa trước và sau khi có sự kiện 

TIST report 2026 

8 

## Hệ thống vé điện tử 

1. Thống kê số hành khách sử dụng tuyến bus tại từng trạm theo các khung thời gian • Phát hiện các trạm hiệu quả 

2. Hiệu quả sử dụng của tuyến theo thời gian 

3. So sánh với tính hiệu đóng mở cửa 

4. Camera trên bus để phát hiện hết ghế ngồi: người đi xe phải đứng ở những trạm bus nào 

TIST report 2026 

9 

## Hệ thống quan trắc môi trường 

1. Các thông số môi trường lấy từ cảm biến đặt trên bus: 

   - Nhiệt độ, độ sáng, độ ẩm, tiếng ồn, tia cực tím (UV) 

   - • Cảm biến rung lắc 

## 2. Camera trên bus 

- Camera ngoài: lưu lượng xe, ổ gà 

- Camera trong: số lượng người trên xe, người đứng không có chổ ngồi 

## 3. Cảm biến ở trạm bus 

   - Cảm biến đo lượng mưa, tiếng ồn 

   - PM2.5, PM10 (bụi mịn), CO (Carbon Monoxide), NO₂ (Nitrogen Dioxide), O₃ (Ozone tầng thấp), VOC (hợp chất hữu cơ bay hơi)??? 

4. Thu nhận dữ liệu quan trắc kết hợp với vị trí bus (GPS), lọc nhiễu, bổ khuyết và vẽ bản đồ thông số môi trường địa phương theo thời gian 

   - Tần suất lấy mẫu, tuyến bus nào, chuyến bus nào và nên gắn thiết bị trên xe nào để tối ưu chi phí nhất 

TIST report 2026 

10 

## Bus điện 

1. Đo lường mức tiêu thụ nhiên liệu hoặc điện của xe bus 

   - Đánh giá lợi ích khi chuyển từ diesel sang điện/hybrid 

   - Mô phỏng tác động môi trường (CO2 reduction) 

2. Ưu tiên chuyển đổi những tuyến bus nào sang dùng bus điện 

3. Đặt trạm sạt ở đâu cho hệ thống bus điện 

TIST report 2026 

11 

## Thank you! 

12 

TIST report 2026 

## Bài toán 

1. Xử lý dữ liệu streaming cho nhiều dữ liệu Bus GPS 

2. Bài toán phân tích cho 1 bus, 1 tuyến nâng lên nhiều (tất cả) bus/ tuyến 

TIST report 2026 

13 

## 2D Data 

https://atlas.cid.harvard.edu/ 

TIST report 2026 

14 

## Multi-Dimensional Data 

TIST report 2026 

15 

## Số tuyến bus trên từng đoạn đường 

TIST report 2026 

16 

## Heatmap transportation 

https://bus.dev.tris.vn 

https://www.researchgate.net/publication/ 342784728_The_visual_analytics_of_big_open_public 

_transport_data_- 

_a_framework_and_pipeline_for_monitoring_system 

_performance_in_Greater_Sydney 

TIST report 2026 

17 

