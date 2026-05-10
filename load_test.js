import http from "k6/http";
import { check, sleep } from "k6";

// تنظیمات حمله (مدیریت موج ترافیک)
export const options = {
  stages: [
    { duration: "10s", target: 100 }, // در 10 ثانیه اول، تعداد کاربران را به 100 نفر برسان
    { duration: "30s", target: 500 }, // برای 30 ثانیه، 500 کاربر همزمان را حفظ کن (نقطه فشار)
    { duration: "10s", target: 0 }, // در 10 ثانیه آخر، کاربران را به صفر برسان
  ],
};

export default function () {
  // شناسه سروری که در دیتابیس ثبت کردید (اگر UUID شما فرق دارد اینجا تغییر دهید)
  const payload = JSON.stringify({
    node_id: "8a38b2d1-0c77-44da-8669-0f0e81c00ba2",
    metric_type: "cpu_usage_stress_test",
    value: Math.random() * 100, // تولید عدد تصادفی برای مصرف CPU
  });

  const params = {
    headers: {
      "Content-Type": "application/json",
    },
  };

  // ارسال درخواست به بک‌اند (از طریق شبکه داخلی داکرِ سیستم میزبان)
  // تغییر به آدرس شبکه داخلی داکر
  const res = http.post("http://backend:8000/metrics_ingest/", payload, params);

  // بررسی اینکه آیا درخواست با موفقیت ثبت شد یا سرور خطا داد؟
  check(res, { "status was 200": (r) => r.status == 200 });

  // یک تاخیر بسیار کوتاه برای شبیه‌سازی رفتار طبیعی‌ترِ شبکه
  sleep(0.05);
}
