# File Watcher Test — Easy Method (2 Terminals)

⚠️ Watcher real-time monitor karta hai, isliye 2 terminals use karne hain.

🧭 STEP 1 — Terminal 1 kholo (Watcher Run karna hai)

# Yahan watcher run hoga jo folder ko watch karega.

`cd /mnt/c/Users/user/Desktop/AI_Employee_Vault/phase1_bronze/`


# Ab watcher run karo:

`timeout 15s python3 Watchers/inbox_watcher.py`

# Iska matlab:

Watcher 15 seconds tak Inbox folder dekhega

Agar koi new file ayi → detect karega

Ab is terminal ko aise hi chhor do
❌ Isme kuch aur mat likhna.

🧭 STEP 2 — Terminal 2 kholo (Test File Create karni hai)

Naya terminal open karo (important!).

Phir same folder me jao:

`cd /mnt/c/Users/user/Desktop/AI_Employee_Vault/phase1_bronze/`

🧭 STEP 3 — Test File Create karo

# Ab ye command run karo:

echo "# My Test Task

This is a sample task for testing.

- Task item 1
- Task item 2" > Inbox/my_task.md

# Ye kya karega?

👉 Inbox folder me ek new file banegi:

Inbox/my_task.md

🧭 STEP 4 — Watcher ka Reaction Dekho (Terminal 1 me)

Ab Terminal 1 (jo watcher chal raha tha) me dekho.

Tumhein kuch aisa output milega:

Detected new file: my_task.md
Processing...
Duplicate check passed


✅ Iska matlab watcher successfully kaam kar raha hai.

🧭 STEP 5 — Confirm File Exist karti hai

# Terminal 2 me run karo:

`ls -la Inbox/`


# Tumhein dikhega:

my_task.md

🧭 STEP 6 — Cleanup (Test File Delete)
rm Inbox/my_task.md

🎯 Expected Result (Teacher ko kya dikhana hai)

Tumhara system:

✔ Folder monitor kar raha hai
✔ New file detect karta hai
✔ Duplicate create nahi karta
✔ Real-time automation working hai

Ye Phase 1 Bronze ka core requirement hai.