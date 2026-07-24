from portal.models import Newsletter

sample_body = """<div class="newsletter-content-styled">
  <div class="newsletter-content-styled">

  <div class="content-card">
    <p>💙 <strong>Dear Esteemed Parents/Guardians,</strong></p>
    <p>As we bring the 2025/2026 Academic Session to a successful close, we sincerely appreciate your unwavering support, trust, and partnership with Divine Triumph International School.</p>
    <p>Your encouragement, cooperation, and commitment have contributed immensely to the success of our learners and the continued growth of our school. Thank you for believing in us and for giving us the privilege of nurturing your children.</p>
  </div>

  <div class="content-card">
    <div class="card-badge-title"><span class="badge-icon">🌟</span><h3>Session Highlights</h3></div>
    <p>During the term, our learners actively participated in:</p>
    <div class="activity-grid">
      <div class="activity-pill">🧮 Mathematics Quiz Competition</div>
      <div class="activity-pill">🔤 Spelling Bee Competition</div>
      <div class="activity-pill">🍳 Home Economics Practical Sessions</div>
      <div class="activity-pill">🎉 Children's Day Celebration</div>
      <div class="activity-pill">👧 International Day of the Girl Child Celebration</div>
    </div>
    <p>These activities helped to develop confidence, creativity, teamwork, leadership, and practical life skills while making learning enjoyable.</p>
  </div>

  <div class="content-card summer-card">
    <div class="card-header-flex">
      <div class="card-badge-title"><span class="badge-icon">☀️</span><h3>2026 Summer Lesson</h3></div>
      <span class="price-tag">₦7,000</span>
    </div>
    <div class="schedule-box">
      <div class="schedule-item"><span class="label">📅 Date</span><span class="value">Mon 3rd – Thu 27th Aug, 2026</span></div>
      <div class="schedule-item"><span class="label">🗓 Days</span><span class="value">Monday – Thursday</span></div>
      <div class="schedule-item"><span class="label">🕘 Time</span><span class="value">9:00 a.m. – 1:00 p.m.</span></div>
    </div>
    <p><strong>✨ Learners will enjoy:</strong></p>
    <ul class="feature-checklist">
      <li>✅ Intensive Academic Lessons</li>
      <li>♟️ Chess</li>
      <li>🔠 Scrabble</li>
      <li>🎲 Indoor Games</li>
      <li>⚽ Outdoor Games</li>
      <li>🎯 Fun &amp; Educational Activities</li>
    </ul>
    <p>Give your child a rewarding and enjoyable holiday experience!</p>
  </div>

  <div class="content-card">
    <div class="card-badge-title"><span class="badge-icon">📝</span><h3>Entrance Examination</h3></div>
    <p>Admission into <strong>ALL CLASSES</strong> for the 2026/2027 Academic Session will be held on:</p>
    <div class="date-chips-container">
      <div class="date-chip"><span class="chip-day">Saturday</span><span class="chip-date">18th July, 2026</span></div>
      <div class="date-chip"><span class="chip-day">Saturday</span><span class="chip-date">8th August, 2026</span></div>
      <div class="date-chip"><span class="chip-day">Friday</span><span class="chip-date">4th September, 2026</span></div>
    </div>
    <div class="recommendation-box">
      <p>📢 Kindly recommend Divine Triumph International School to your friends, neighbours, relatives, and colleagues seeking quality education for their children.</p>
    </div>
  </div>

  <div class="content-card">
    <div class="resumption-banner">
      <div class="resumption-title">🔔 RESUMPTION DATE</div>
      <div class="resumption-session">2026/2027 Academic Session</div>
      <div class="resumption-date-highlight">Monday, 7th September, 2026</div>
    </div>
    <p>We look forward to welcoming all our learners back, refreshed and ready for another successful academic year.</p>
  </div>

  <div class="content-card">
    <div class="card-badge-title"><span class="badge-icon">💐</span><h3>Holiday Message</h3></div>
    <p>The Management and Staff of Divine Triumph International School wish you and your family a peaceful, safe, and refreshing holiday.</p>
    <p>Thank you for being a valued member of the Divine Triumph International School family. We look forward to seeing all our learners in the new academic session.</p>
    <div class="signoff-block">
      <span class="signoff-name">Mr. Bright Uzoma</span>
      <span class="signoff-role">Principal, Junior Secondary School</span>
      <span class="signoff-school">Divine Triumph International School</span>
    </div>
  </div>

</div>
</div>"""

Newsletter.objects.update_or_create(
    slug="welcome-newsletter",
    defaults={
        "title": "END-OF-SESSION NEWSLETTER",
        "academic_session": "2025/2026 ACADEMIC SESSION",
        "summary": "As we bring the 2025/2026 Academic Session to a successful close, we sincerely appreciate your unwavering support, trust, and partnership with Divine Triumph International School.",
        "body": sample_body,
        "published": True,
    },
)
print("Newsletter created/updated successfully!")
