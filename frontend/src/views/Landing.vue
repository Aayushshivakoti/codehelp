<template>
  <div class="landing-container">
    <nav class="navbar">
      <div class="nav-brand">
        <span class="brand-icon">⚡</span>
        <span class="brand-name">FitLife Programming</span>
      </div>
      <div class="nav-actions">
        <router-link to="/guest/sandbox" class="nav-link">Code Sandbox</router-link>
        <router-link to="/login" class="btn-login">Sign In</router-link>
      </div>
    </nav>

    <header class="hero">
      <div class="hero-content">
        <div class="badge">Adaptive Learning Assessment</div>
        <h1>Elevate Your Code <br><span class="gradient-text">Master Your Skills</span></h1>
        <p class="hero-subtitle">
          An intelligent web-based programming assessment platform. Test your skills, track your progress with advanced analytics, and earn achievements.
        </p>
        <div class="hero-cta">
          <router-link to="/login" class="btn-primary">Start Assessment</router-link>
          <router-link to="/guest/sandbox" class="btn-secondary">Try Coding Sandbox</router-link>
        </div>
      </div>
      <div class="hero-visual">
        <div class="code-preview">
          <div class="preview-header">
            <span class="dot red"></span>
            <span class="dot yellow"></span>
            <span class="dot green"></span>
            <span class="file-name">assessment.js</span>
          </div>
          <pre><code><span class="keyword">const</span> assessment = {
  name: <span class="string">"Web Development"</span>,
  level: <span class="string">"Advanced"</span>,
  topics: [<span class="string">"HTML"</span>, <span class="string">"CSS"</span>, <span class="string">"JS"</span>],
  adaptive: <span class="keyword">true</span>,
  streak: <span class="number">7</span>
};

<span class="keyword">function</span> <span class="title">recommend</span>(profile) {
  <span class="keyword">if</span> (profile.proficiency &lt; <span class="number">50</span>) {
    <span class="keyword">return</span> <span class="string">"Suggest Basic Review"</span>;
  }
  <span class="keyword">return</span> <span class="string">"Unlock Advanced Chapter"</span>;
}</code></pre>
        </div>
      </div>
    </header>

    <section class="features">
      <h2>Why FitLife Programming?</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">🧠</div>
          <h3>Adaptive Algorithm</h3>
          <p>Dynamically adjusts quiz suggestions based on your performance trends, ensuring you master foundational concepts before advancing.</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🏆</div>
          <h3>Gamified System</h3>
          <p>Earn XP points, maintain daily activity streaks, and unlock unique achievement badges as you progress through different chapters.</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <h3>Advanced Analytics</h3>
          <p>Understand your performance with radar strength metrics and XP velocity logs. Export your records as structured PDF files.</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">💬</div>
          <h3>Community Discussions</h3>
          <p>Stuck on a tricky question? Share solutions, read explanations, and discuss concepts in integrated question discussion boards.</p>
        </div>
      </div>
    </section>

    <footer class="footer">
      <p>&copy; 2026 FitLife Programming Assessment System. All rights reserved.</p>
    </footer>
  </div>
</template>

<script setup>
// Landing page component logic
</script>

<style scoped>
.landing-container {
  min-height: 100vh;
  background-color: #0b0f19;
  color: #f8fafc;
  font-family: 'Inter', sans-serif;
  overflow-x: hidden;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 4rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.brand-icon {
  font-size: 1.5rem;
}

.brand-name {
  font-weight: 700;
  font-size: 1.25rem;
  letter-spacing: -0.025em;
  background: linear-gradient(135deg, #a78bfa 0%, #818cf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-link {
  color: #94a3b8;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.nav-link:hover {
  color: #f8fafc;
}

.btn-login {
  background: linear-gradient(135deg, #6d28d9 0%, #4f46e5 100%);
  color: white;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-login:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6rem 4rem;
  max-width: 1280px;
  margin: 0 auto;
  gap: 4rem;
}

.hero-content {
  flex: 1.2;
}

.badge {
  display: inline-block;
  background: rgba(139, 92, 246, 0.1);
  color: #c084fc;
  padding: 0.375rem 1rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
  border: 1px solid rgba(139, 92, 246, 0.2);
  margin-bottom: 1.5rem;
}

.hero h1 {
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1.15;
  margin-bottom: 1.5rem;
  letter-spacing: -0.03em;
}

.gradient-text {
  background: linear-gradient(135deg, #c084fc 0%, #6366f1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 1.125rem;
  color: #94a3b8;
  line-height: 1.7;
  margin-bottom: 2.5rem;
}

.hero-cta {
  display: flex;
  gap: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%);
  color: white;
  padding: 0.875rem 2rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #f8fafc;
  padding: 0.875rem 2rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: background 0.2s, border 0.2s;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

.hero-visual {
  flex: 0.8;
}

.code-preview {
  background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  font-family: 'Fira Code', monospace;
  overflow: hidden;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot.red { background: #ef4444; }
.dot.yellow { background: #f59e0b; }
.dot.green { background: #10b981; }

.file-name {
  margin-left: 0.5rem;
  color: #64748b;
  font-size: 0.8rem;
}

.code-preview pre {
  margin: 0;
  padding: 1.5rem;
  font-size: 0.9rem;
  line-height: 1.5;
  color: #e2e8f0;
  overflow-x: auto;
}

.keyword { color: #f43f5e; }
.string { color: #10b981; }
.number { color: #f59e0b; }
.title { color: #3b82f6; }

.features {
  padding: 6rem 4rem;
  max-width: 1280px;
  margin: 0 auto;
}

.features h2 {
  text-align: center;
  font-size: 2.25rem;
  font-weight: 800;
  margin-bottom: 4rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.01);
  border: 1px solid rgba(255, 255, 255, 0.04);
  padding: 2rem;
  border-radius: 12px;
  transition: transform 0.2s, background 0.2s, border-color 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.02);
  border-color: rgba(139, 92, 246, 0.3);
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
}

.feature-card p {
  color: #94a3b8;
  font-size: 0.95rem;
  line-height: 1.6;
}

.footer {
  text-align: center;
  padding: 3rem;
  color: #64748b;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 0.9rem;
}

@media (max-width: 1024px) {
  .navbar {
    padding: 1.5rem 2rem;
  }
  .hero {
    flex-direction: column;
    padding: 4rem 2rem;
    text-align: center;
  }
  .hero-cta {
    justify-content: center;
  }
  .code-preview {
    max-width: 500px;
    margin: 0 auto;
  }
  .features {
    padding: 4rem 2rem;
  }
}
</style>
