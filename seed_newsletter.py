from portal.models import Newsletter

sample_body = """💙 Dear Esteemed Parents/Guardians,

As we bring the 2025/2026 Academic Session to a successful close, we sincerely appreciate your unwavering support, trust, and partnership with Divine Triumph International School.

Your encouragement, cooperation, and commitment have contributed immensely to the success of our learners and the continued growth of our school. Thank you for believing in us and for giving us the privilege of nurturing your children.

━━━━━━━━━━━━━━━━━━━━━━━

🌟 SESSION HIGHLIGHTS

During the term, our learners actively participated in:

🧮 Mathematics Quiz Competition
🔤 Spelling Bee Competition
🍳 Home Economics Practical Sessions
🎉 Children's Day Celebration
👧 International Day of the Girl Child Celebration

These activities helped to develop confidence, creativity, teamwork, leadership, and practical life skills while making learning enjoyable.

━━━━━━━━━━━━━━━━━━━━━━━

☀️ 2026 SUMMER LESSON

📅 Date: Monday, 3rd August – Thursday, 27th August, 2026
🗓 Days: Monday – Thursday
🕘 Time: 9:00 a.m. – 1:00 p.m.
💵 Fee: ₦7,000

✨ Learners will enjoy:
✅ Intensive Academic Lessons
♟️ Chess
🔠 Scrabble
🎲 Indoor Games
⚽ Outdoor Games
🎯 Fun & Educational Activities

Give your child a rewarding and enjoyable holiday experience!

━━━━━━━━━━━━━━━━━━━━━━━

📝 ENTRANCE EXAMINATION

Admission into ALL CLASSES for the 2026/2027 Academic Session will be held on:

📅 Saturday, 18th July, 2026
📅 Saturday, 8th August, 2026
📅 Friday, 4th September, 2026

📢 Kindly recommend Divine Triumph International School to your friends, neighbours, relatives, and colleagues seeking quality education for their children.

━━━━━━━━━━━━━━━━━━━━━━━

🔔 RESUMPTION DATE

🏫 2026/2027 Academic Session
📅 Monday, 7th September, 2026

We look forward to welcoming all our learners back, refreshed and ready for another successful academic year.

━━━━━━━━━━━━━━━━━━━━━━━

💐 HOLIDAY MESSAGE

The Management and Staff of Divine Triumph International School wish you and your family a peaceful, safe, and refreshing holiday.

Thank you for being a valued member of the Divine Triumph International School family. We look forward to seeing all our learners in the new academic session.

━━━━━━━━━━━━━━━━━━━━━━━

Mr. Bright Uzoma
Principal
Junior Secondary School

🏫 DIVINE TRIUMPH INTERNATIONAL SCHOOL
Hard Work, Orderliness and Excellence"""

Newsletter.objects.create(
    title="END-OF-SESSION NEWSLETTER",
    academic_session="2025/2026 ACADEMIC SESSION",
    summary="As we bring the 2025/2026 Academic Session to a successful close, we sincerely appreciate your unwavering support, trust, and partnership with Divine Triumph International School.",
    body=sample_body,
    published=True
)

)
print("Sample newsletter successfully created!")