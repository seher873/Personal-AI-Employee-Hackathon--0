# Facebook API Access - Fix Guide

## ❌ Current Problem: "API access blocked"

Token valid hai, Page ID sahi hai, lekin API access blocked hai kyunki:
- App review pending hai
- Ya app "Development Mode" mein hai

---

## ✅ Solution 1: App Ko Live Karo (Quick Fix)

### Step 1: App Dashboard kholo
```
https://developers.facebook.com/apps/781070051729264/settings/basic/
```

### Step 2: App Mode check karo
- **App Mode** dikhega: "Development" ya "Live"
- Agar "Development" hai, toh **"Switch to Live"** pe click karo

### Step 3: Category select karo
- App Category select karo (e.g., "Business")
- Save karo

### Step 4: Privacy Policy URL (optional for now)
- Abhi ke liye skip kar sakte ho
- Baad mein add kar lena

---

## ✅ Solution 2: Testers Add Karo (Development Mode mein)

Agar app Live nahi karna chahte, toh:

### Step 1: App Dashboard
```
https://developers.facebook.com/apps/781070051729264/roles/test-users/
```

### Step 2: Add Test User
- "Add" button pe click karo
- Apna Facebook account (urojk77@gmail.com) add karo
- Save karo

### Step 3: Naya Token banao
- Graph Explorer mein jao
- Naya Page Access Token generate karo
- Ab kaam karega!

---

## ✅ Solution 3: App Review Submit Karo (Long-term)

### Step 1: App Review Dashboard
```
https://developers.facebook.com/apps/781070051729264/app-review/submissions/
```

### Step 2: Permissions add karo
Click "Add for Review" aur yeh permissions select karo:
- `pages_manage_posts`
- `pages_read_engagement`
- `pages_show_list`
- `instagram_basic`
- `instagram_content_publish`

### Step 3: Details bharo
- Har permission ke liye explanation likho
- Screenshots/video upload karo
- Submit karo

### Step 4: Approval wait karo
- 2-7 days lagte hain
- Email aayega jab approve hoga

---

## 🚀 Quick Test (Abhi ke liye)

**Professional Dashboard se check karo:**

1. **Page Access check karo:**
```
https://www.facebook.com/professional_dashboard
```
- Left side mein "Pages" pe click karo
- "uroj's online page" select karo
- "Access" check karo - tumhare paas "Full Control" hona chahiye

2. **Instagram connect karo:**
```
https://www.facebook.com/accounts/
```
- Instagram account connect karo apne Page se
- Instagram Business account hona chahiye

3. **Naya token banao:**
```
https://developers.facebook.com/tools/explorer/
```
- Get Token → Get Page Access Token
- "uroj's online page" select karo
- Naya token copy karo

4. **Mujhe bhejo:**
- Naya Page Access Token
- Main `.env` update karke test karta hoon

---

## 📋 Checklist

- [ ] App Dashboard mein jao
- [ ] App Mode "Live" karo YA Testers add karo
- [ ] Naya Page Access Token banao
- [ ] Token share karo
- [ ] Test karo

---

## 🔗 Important Links

| Kaam | Link |
|------|------|
| App Dashboard | https://developers.facebook.com/apps/781070051729264/ |
| App Settings | https://developers.facebook.com/apps/781070051729264/settings/basic/ |
| App Review | https://developers.facebook.com/apps/781070051729264/app-review/submissions/ |
| Graph Explorer | https://developers.facebook.com/tools/explorer/ |
| Professional Dashboard | https://www.facebook.com/professional_dashboard |
| Page Access | https://www.facebook.com/pages/ |

---

## ❓ Help Chahiye?

Screenshot bhejo ya batao:
1. App Dashboard mein kya dikh raha hai?
2. App Mode kya hai? (Development/Live)
3. Koi error message?
