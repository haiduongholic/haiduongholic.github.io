# Hải Dương Holic – Portfolio

Portfolio review TikTok của kênh [@haiduongholic](https://www.tiktok.com/@haiduongholic).
Số liệu (follower, lượt thích, số bài, lượt xem từng video) tự cập nhật mỗi giờ bằng GitHub Actions.

- `haiduongholic.html` – nội dung trang (sửa giao diện ở đây)
- `update_stats.py` – lấy số liệu mới từ TikTok, ghi vào khối `hdh-data` trong trang
- `build_export.py` – dựng `docs/index.html` (trang GitHub Pages) và `docs/HaiDuongHolic-Portfolio.html` (bản tải về, ảnh nhúng sẵn)
- `.github/workflows/update-stats.yml` – lịch chạy mỗi giờ; vào tab **Actions → Cập nhật số liệu TikTok → Run workflow** để cập nhật ngay

Muốn theo dõi thêm video: thêm ID video vào `views` trong khối `hdh-data` và vào danh sách `TOP` hoặc `V` trong `haiduongholic.html`.
