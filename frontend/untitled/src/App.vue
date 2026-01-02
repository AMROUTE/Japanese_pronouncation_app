<template>
  <div id="app">
    <!-- 课程选择页面 -->
    <div v-if="!currentCategory" class="course-selection">
      <h1 class="title">日语口语练习</h1>
      <p class="subtitle">选择一个课程开始练习</p>
      <div class="stats-section" v-if="stats.totalAttempts > 0">
        <h2>我的学习进度</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ stats.totalPracticed }}</div>
            <div class="stat-label">已练习句子</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.averageScore }}%</div>
            <div class="stat-label">平均匹配度</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.bestScore }}%</div>
            <div class="stat-label">最高记录</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.totalAttempts }}</div>
            <div class="stat-label">总练习次数</div>
          </div>
        </div>

        <h3 style="margin-top: 40px;">最近练习</h3>
        <div class="recent-list">
          <div v-for="record in stats.recentRecords.slice(0,5)" :key="record.date + record.japanese" class="recent-item">
            <span class="sentence">{{ record.japanese }} ({{ record.romaji }})</span>
            <span class="score">{{ record.score }}%</span>
            <span class="date">{{ record.date }}</span>
          </div>
        </div>
      </div>

      <!-- 第一次使用鼓励 -->
      <div v-else class="welcome-stats">
        <h2>欢迎开始日语口语之旅！🌸</h2>
        <p>完成第一次练习后，这里将显示你的学习进度</p>
      </div>
      <div class="course-grid">
        <div class="course-card" @click="selectCategory('greeting')">
          <h3>🌤️ 日常问候</h3>
          <p>问好、打招呼、询问近况</p>
          <span class="tag success">5 句</span>
        </div>
        <div class="course-card" @click="selectCategory('introduction')">
          <h3>👋 自我介绍</h3>
          <p>名字、职业、初次见面</p>
          <span class="tag primary">4 句</span>
        </div>
        <div class="course-card" @click="selectCategory('thanks')">
          <h3>🙏 感谢与道歉</h3>
          <p>谢谢、对不起、不客气</p>
          <span class="tag warning">4 句</span>
        </div>
      </div>
    </div>

    <!-- 练习页面 -->
    <div v-else class="practice-mode">
      <div class="header-bar">
        <button class="back-btn" @click="backToCourses">← 返回课程</button>
        <h2>{{ categoryName }}</h2>
      </div>

      <div v-if="loading" class="loading">加载句子中...</div>

      <div v-else class="practice-card">
        <div class="phrase-content">
          <div class="japanese">{{ phrase.japanese }}</div>
          <div class="romaji">{{ phrase.romaji }}</div>
          <div class="english">{{ phrase.english }}</div>

          <!-- TTS 标准发音按钮（用 emoji，避免图标问题） -->
          <div class="tts-control">
            <button
                class="tts-btn"
                @click="playStandardPronunciation"
                :disabled="isSpeaking"
            >
              {{ isSpeaking ? '⏳ 播放中...' : '🔊 听标准发音' }}
            </button>
          </div>
        </div>

        <!-- 评分区域 -->
        <div v-if="lastScore > -1" class="score-section">
          <div class="score-label">匹配度</div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: lastScore + '%', background: scoreColor }"></div>
            <span class="percent">{{ lastScore }}%</span>
          </div>
          <div class="score-message">{{ scoreMessage }}</div>
        </div>

        <!-- 控制按钮 -->
        <div class="controls">
          <button
              v-if="!isRecording"
              class="btn primary round"
              @click="startRecording"
              :disabled="!supportsSpeech || isProcessing"
          >
            🎤 开始录音
          </button>
          <button v-else class="btn danger round" @click="stopRecording">
            ⏹ 停止录音
          </button>

          <button class="btn success" @click="getNewPhrase">下一句</button>
          <button class="btn info" @click="retryCurrent">重练本句</button>
        </div>
        <!-- 实时识别文字（录音中显示） -->
        <div v-if="isRecording && recognizedText" class="live-text">
          <p>实时识别：</p>
          <p class="live-recognized">{{ recognizedText }} <span class="cursor">|</span></p>
        </div>
        <!-- 识别结果 -->
        <div v-if="recognizedText" class="result">
          <p>你说的是：</p>
          <p class="recognized-text">{{ recognizedText }}</p>
        </div>

        <!-- 录音回放 -->
        <div v-if="audioURL" class="playback">
          <p>你的录音回放</p>
          <audio controls :src="audioURL" class="audio"></audio>
          <button class="clear-btn" @click="clearRecording">清除录音</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      currentCategory: null,
      categoryName: '',
      phrase: null,
      recognizedText: '',
      lastScore: -1,
      isRecording: false,
      isProcessing: false,
      loading: false,
      recognition: null,
      mediaRecorder: null,
      audioChunks: [],
      audioURL: '',
      supportsSpeech: false,
      isSpeaking: false,
      utterance: null,showStats: true,  // 是否显示进度统计（可做按钮切换）
      stats: {
        totalPracticed: 0,
        totalAttempts: 0,
        averageScore: 0,
        bestScore: 0,
        recentRecords: []  // [{japanese, score, date}]
      }
    }
  },
  computed: {
    scoreColor() {
      if (this.lastScore >= 80) return '#67c23a'
      if (this.lastScore >= 60) return '#e6a23c'
      return '#f56c6c'
    },
    scoreMessage() {
      if (this.lastScore >= 90) return '完美！🎉'
      if (this.lastScore >= 80) return '非常棒！👍'
      if (this.lastScore >= 60) return '继续加油！💪'
      return '再试一次哦～'
    }
  },
  created() {
    this.checkSpeechSupport()
    this.loadStatsFromStorage()
  },
  methods: {
    checkSpeechSupport() {
      this.supportsSpeech = 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window
    },
    selectCategory(category) {
      const names = {
        greeting: '日常问候',
        introduction: '自我介绍',
        thanks: '感谢与道歉'
      }
      this.currentCategory = category
      this.categoryName = names[category]
      this.getNewPhrase()
    },
    backToCourses() {
      this.currentCategory = null
      this.phrase = null
      this.recognizedText = ''
      this.lastScore = -1
      this.clearRecording()
    },
    async getNewPhrase() {
      this.loading = true
      this.recognizedText = ''
      this.lastScore = -1
      this.clearRecording()
      try {
        const res = await fetch(`http://127.0.0.1:8000/get_phrase/${this.currentCategory}`)
        if (!res.ok) throw new Error()
        this.phrase = await res.json()
      } catch (err) {
        alert('无法连接后端，请确保后端正在运行')
      } finally {
        this.loading = false
      }
    },
    retryCurrent() {
      this.recognizedText = ''
      this.lastScore = -1
      this.clearRecording()
    },
    async startRecording() {
      if (this.isRecording || this.isProcessing) return
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        this.mediaRecorder = new MediaRecorder(stream)
        this.audioChunks = []

        this.mediaRecorder.ondataavailable = e => this.audioChunks.push(e.data)
        this.mediaRecorder.onstop = () => {
          const blob = new Blob(this.audioChunks, { type: 'audio/webm' })
          this.audioURL = URL.createObjectURL(blob)
          stream.getTracks().forEach(t => t.stop())
        }

        this.mediaRecorder.start()
        this.isRecording = true

        const Rec = window.SpeechRecognition || window.webkitSpeechRecognition
        this.recognition = new Rec()
        this.recognition.lang = 'ja-JP'
        this.recognition.continuous = true
        this.recognition.interimResults = true

        this.recognition.onresult = event => {
          let interimTranscript = ''
          let finalTranscript = ''

          // 遍历所有结果
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript
            if (event.results[i].isFinal) {
              finalTranscript += transcript
            } else {
              interimTranscript += transcript
            }
          }

          // 最终文字 + 临时文字（临时文字用灰色显示）
          this.recognizedText = finalTranscript + interimTranscript
        }

        this.recognition.start()
      } catch (err) {
        alert('无法访问麦克风')
      }
    },
    stopRecording() {
      if (!this.isRecording) return
      this.isProcessing = true

      if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
        this.mediaRecorder.stop()
      }
      if (this.recognition) {
        this.recognition.stop()
      }

      this.isRecording = false

      // 关键修复：延迟1秒确保识别引擎完成最终结果，然后强制评分
      setTimeout(() => {
        // 如果有任何识别文字，就强制计算分数
        if (this.recognizedText && this.recognizedText.trim() !== '') {
          this.calculateScore()
          this.$message && this.$message.success && this.$message.success('评分完成！可以再录一次提升分数哦～')
        } else {
          this.$message && this.$message.info && this.$message.info('未检测到语音，请再说一次')
        }
        this.isProcessing = false
      }, 1200)  // 延长到1200ms，更保险
    },
    clearRecording() {
      if (this.audioURL) URL.revokeObjectURL(this.audioURL)
      this.audioURL = ''
      this.audioChunks = []
    },
    calculateScore() {
      if (!this.phrase) {
        console.warn('无当前句子，无法评分')
        return
      }
      if (!this.recognizedText || this.recognizedText.trim() === '') {
        this.lastScore = 0
        return
      }

      // 优先 hiragana，其次 japanese
      let target = (this.phrase.hiragana || this.phrase.japanese || '').trim()
      if (target === '') {
        console.warn('目标句子为空')
        this.lastScore = 0
        return
      }

      target = target.replace(/[！？。、，,.!?]/g, '').replace(/\s/g, '')
      const said = this.recognizedText.replace(/[！？。、，,.!?]/g, '').replace(/\s/g, '')

      const similarity = this.stringSimilarity(target, said)
      this.lastScore = Math.round(similarity * 100)

      console.log(`评分成功：目标 "${target}" vs 识别 "${said}" → ${this.lastScore}%`)
    },
    stringSimilarity(s1, s2) {
      const longer = s1.length > s2.length ? s1 : s2
      const shorter = s1.length > s2.length ? s2 : s1
      if (longer.length === 0) return 1
      return (longer.length - this.editDistance(longer, shorter)) / longer.length
    },
    editDistance(s1, s2) {
      const costs = []
      for (let i = 0; i <= s1.length; i++) {
        costs[i] = [i]
        for (let j = 1; j <= s2.length; j++) {
          costs[i][j] = s1[i-1] === s2[j-1]
              ? costs[i-1][j-1]
              : Math.min(costs[i-1][j], costs[i][j-1], costs[i-1][j-1]) + 1
        }
      }
      return costs[s1.length][s2.length]
    },
    playStandardPronunciation() {
      if (!('speechSynthesis' in window)) {
        alert('你的浏览器不支持语音播放')
        return
      }
      if (this.isSpeaking) {
        speechSynthesis.cancel()
        this.isSpeaking = false
        return
      }
      const text = this.phrase.japanese
      this.utterance = new SpeechSynthesisUtterance(text)
      this.utterance.lang = 'ja-JP'
      this.utterance.rate = 0.9

      this.utterance.onstart = () => this.isSpeaking = true
      this.utterance.onend = () => this.isSpeaking = false
      this.utterance.onerror = () => this.isSpeaking = false

      speechSynthesis.cancel()
      speechSynthesis.speak(this.utterance)
    },
    loadStatsFromStorage() {
      const saved = localStorage.getItem('japanesePracticeStats')
      if (saved) {
        this.stats = JSON.parse(saved)
      }
    },
    saveStatsToStorage() {
      localStorage.setItem('japanesePracticeStats', JSON.stringify(this.stats))
    },
    updateStatsAfterPractice() {
      if (this.lastScore < 0) return

      this.stats.totalAttempts += 1
      this.stats.totalPracticed = new Set([
        ...this.stats.recentRecords.map(r => r.japanese),
        this.phrase.japanese
      ]).size

      // 更新平均分
      const totalScore = this.stats.averageScore * (this.stats.totalAttempts - 1) + this.lastScore
      this.stats.averageScore = Math.round(totalScore / this.stats.totalAttempts)

      // 更新最高分
      if (this.lastScore > this.stats.bestScore) {
        this.stats.bestScore = this.lastScore
      }

      // 添加最近记录（最多保留10条）
      this.stats.recentRecords.unshift({
        japanese: this.phrase.japanese,
        romaji: this.phrase.romaji,
        score: this.lastScore,
        date: new Date().toLocaleDateString('zh-CN')
      })
      if (this.stats.recentRecords.length > 10) {
        this.stats.recentRecords.pop()
      }

      this.saveStatsToStorage()
    },
  }
}
</script>

<style scoped>
#app {
  min-height: 100vh;
  background: #f5f7fa;
  font-family: 'Noto Sans JP', -apple-system, sans-serif;
  padding: 20px;
  color: #333;
}

.course-selection {
  max-width: 1000px;
  margin: 0 auto;
  text-align: center;
  padding-top: 60px;
}

.title {
  font-size: 2.8rem;
  margin-bottom: 16px;
}

.subtitle {
  font-size: 1.3rem;
  color: #888;
  margin-bottom: 60px;
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 30px;
}

.course-card {
  background: white;
  border-radius: 16px;
  padding: 30px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transition: transform 0.3s;
}

.course-card:hover {
  transform: translateY(-10px);
}

.course-card h3 {
  font-size: 1.6rem;
  margin: 20px 0 10px;
}

.tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  color: white;
}

.success { background: #67c23a; }
.primary { background: #409eff; }
.warning { background: #e6a23c; }

.practice-mode {
  max-width: 800px;
  margin: 0 auto;
}

.header-bar {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}

.back-btn {
  background: none;
  border: none;
  font-size: 1.4rem;
  cursor: pointer;
  padding: 10px;
}

.header-bar h2 {
  flex: 1;
  text-align: center;
  margin: 0;
  font-size: 1.8rem;
  color: #333;
}

.practice-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.phrase-content {
  text-align: center;
  margin-bottom: 40px;
}

.japanese {
  font-size: 4rem;
  font-weight: bold;
  color: #409eff;
  margin: 20px 0;
}

.romaji {
  font-size: 1.8rem;
  color: #888;
  font-style: italic;
}

.english {
  font-size: 1.4rem;
  color: #666;
  margin-top: 20px;
}

.tts-control {
  margin-top: 30px;
}

.tts-btn {
  padding: 12px 30px;
  font-size: 1.2rem;
  background: #ffb74d;
  color: white;
  border: none;
  border-radius: 50px;
  cursor: pointer;
}

.controls {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
  margin: 40px 0;
}

.btn {
  padding: 14px 28px;
  font-size: 1.1rem;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  min-width: 140px;
}

.primary { background: #409eff; color: white; }
.danger { background: #f56c6c; color: white; }
.success { background: #67c23a; color: white; }
.info { background: #909399; color: white; }
.round { border-radius: 50px; }

.score-section {
  text-align: center;
  margin: 40px 0;
}

.score-label {
  font-size: 1.3rem;
  color: #666;
  margin-bottom: 15px;
}

.progress-bar {
  position: relative;
  height: 30px;
  background: #ebeef5;
  border-radius: 15px;
  overflow: hidden;
  margin: 20px 0;
}

.progress-fill {
  height: 100%;
  transition: width 0.6s ease;
  border-radius: 15px;
}

.percent {
  position: absolute;
  width: 100%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.4rem;
  font-weight: bold;
  color: #333;
}

.score-message {
  font-size: 1.6rem;
  font-weight: bold;
  margin-top: 20px;
}

.result, .playback {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  margin: 30px 0;
}

.recognized-text {
  font-size: 1.6rem;
  color: #409eff;
  font-weight: 500;
  margin-top: 10px;
}

.audio {
  width: 100%;
  max-width: 500px;
  margin: 15px 0;
}

.clear-btn {
  background: none;
  border: none;
  color: #909399;
  cursor: pointer;
  margin-top: 10px;
}

.loading {
  text-align: center;
  font-size: 1.4rem;
  color: #999;
  padding: 100px 0;
}

.live-text {
  text-align: center;
  padding: 20px;
  background: #e6f7ff;
  border-radius: 12px;
  margin: 30px 0;
  border: 2px dashed #91d5ff;
}

.live-recognized {
  font-size: 2rem;
  color: #096dd9;
  font-weight: bold;
  margin-top: 10px;
  min-height: 60px;
}

.cursor {
  animation: blink 1s infinite;
  opacity: 1;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* 录音中临时文字变灰（可选美化） */
.live-recognized::after {
  content: '';
}

.stats-section {
  margin: 60px 0;
  text-align: center;
}

.stats-section h2 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 30px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-item {
  background: white;
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.stat-value {
  font-size: 2.8rem;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 1.1rem;
  color: #666;
  margin-top: 10px;
}

.recent-list {
  max-width: 600px;
  margin: 0 auto;
  text-align: left;
}

.recent-item {
  padding: 15px;
  background: white;
  border-radius: 12px;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.sentence {
  flex: 1;
  font-weight: 500;
}

.score {
  font-size: 1.4rem;
  font-weight: bold;
  color: #67c23a;
  margin: 0 20px;
}

.date {
  color: #999;
  font-size: 0.9rem;
}

.welcome-stats {
  margin: 80px 0;
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.welcome-stats h2 {
  font-size: 2.2rem;
  color: #409eff;
  margin-bottom: 20px;
}
</style>