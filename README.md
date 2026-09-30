
# 🎸 ChordsEngine Windows

### מילים ואקורדים. ישירות מהשיר.

**תוכנת Windows לניתוח שירים, תמלול מילים וזיהוי אקורדים לגיטרה — מקומית ובאופן לא מקוון.**

**Windows software for song lyrics, transcription and guitar chord detection — running locally with whisper.cpp.**

<br>

[**⬇️ הורדות / Downloads**](https://github.com/unisocsu/chords-engine-windows/releases) ·
[**📦 GitHub Repository**](https://github.com/unisocsu/chords-engine-windows)

<br>

![Windows](https://img.shields.io/badge/Windows-64--bit-0078D4?logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Whisper](https://img.shields.io/badge/Whisper-whisper.cpp-8A2BE2)
![Offline](https://img.shields.io/badge/Processing-Offline-2EA44F)


---

## 🇮🇱 מה זה?

**ChordsEngine Windows** היא תוכנה ל-Windows שמנתחת קובצי שירים ומפיקה מהם דף עם **מילים, אקורדים ומידע מוזיקלי**.

העיבוד מתבצע על המחשב המקומי באמצעות מנועי אודיו ו־Whisper, כך שלאחר ההתקנה והגדרת המודל ניתן לעבוד באופן מקומי.

### ✨ יכולות

| | יכולת |
|---|---|
| 🎵 | תמלול מילות השיר |
| 🎸 | זיהוי אקורדים לגיטרה |
| 🎼 | זיהוי סולם |
| 🥁 | קצב ופעמות |
| 📝 | הצמדת אקורדים למילים לפי זמן |
| 🔄 | טרנספוזיציה |
| 🎹 | מידע על אצבועי גיטרה ופסנתר |
| 🎛️ | הצעות קאפו |
| 💾 | ספרייה מקומית לשירים שנותחו |
| 📴 | עיבוד מקומי ללא צורך בחיבור לאינטרנט לאחר ההתקנה |

---

## 🪟 מהדורות Windows

בכל Build נבנות **5 מהדורות**:

| מהדורה | מודל | מתאים ל־ |
|---|---|---|
| **Tiny** | כלול | התקנה קטנה יותר |
| **Base** | כלול | שימוש קליל |
| **Small** | כלול | איזון בין גודל לאיכות |
| **Medium** | כלול | איכות תמלול גבוהה יותר |
| **No Model** | לא כלול | למי שכבר יש מודל |

### 📦 כל מהדורה מגיעה כ־Installer

אין צורך להתקין Python כדי להשתמש בגרסאות ה־EXE המוכנות.

במהדורת **No Model** המתקין מאפשר לבחור קובץ Whisper קיים ולהעתיק אותו לתיקיית התוכנה. המתקין יוצר גם קיצור דרך בתפריט התחל ובשולחן העבודה.


### 🚀 רוצה לנסות?

[**⬇️ עבור לכל ההורדות ב־GitHub Releases**](https://github.com/unisocsu/chords-engine-windows/releases)

---

## ⚙️ איך זה עובד?

ChordsEngine משלב מספר רכיבים:

- **whisper.cpp** — תמלול האודיו וזיהוי מילים וזמנים.
- **lv-chordia** — זיהוי אקורדים.
- **librosa** — ניתוח קצב ופעמות.
- **PyAV / FFmpeg** — פענוח קובצי שמע ווידאו.
- מנוע Python שמחבר את תוצאות הניתוח ומפיק דף אקורדים.

---

## 🛠️ טכנולוגיות

**Python · whisper.cpp · Whisper · lv-chordia · librosa · PyAV · FFmpeg · pywebview · WebView2**

---

## 👨‍💻 פיתוח

להרצה מסביבת Python:

```bash
pip install -r requirements.txt
python scripts/setup_vendor.py
python -m chords_engine serve
```

ניתוח קובץ שמע:

```bash
python -m chords_engine analyze song.mp3 --out out
```

בדיקות:

```bash
python -m unittest discover tests
```

---

## 🌍 שפות

הפרויקט מתוכנן לתמוך בשפות נוספות בהמשך הפיתוח.

---

## 🇬🇧 English

### What is ChordsEngine?

**ChordsEngine Windows** is Windows software for analyzing songs and generating lyrics and guitar-chord sheets.

It combines local audio processing, **whisper.cpp** transcription and chord analysis to produce useful musical information from songs.

### Features

- 🎵 Song lyrics transcription
- 🎸 Guitar chord detection
- 🎼 Musical key detection
- 🥁 Tempo and beat information
- 📝 Time-aligned chords
- 🔄 Chord transposition
- 🎹 Guitar and piano fingering information
- 🎛️ Capo suggestions
- 💾 Local song library
- 📴 Local/offline processing

### Windows Editions

| Edition | Model | Description |
|---|---|---|
| **Tiny** | Bundled | Smallest bundled-model edition |
| **Base** | Bundled | Lightweight edition |
| **Small** | Bundled | Balanced size and quality |
| **Medium** | Bundled | Higher transcription quality |
| **No Model** | Not bundled | Select an existing model during installation |

All packaged editions are distributed as **Windows EXE installers** and do not require Python on the user's computer.

---

## 🙏 Credits

**ChordsEngine Windows** is a fork and continued development of the original chord-and-lyrics engine built with **Claude Code by [@tsoolgee](https://github.com/tsoolgee)**.

The Windows packaging, EXE editions, installers, GitHub Actions build pipeline and continued development are maintained in this repository.

Original project attribution is intentionally preserved.

---

<div align="center">

**🎸 ChordsEngine Windows**

[**Download**](https://github.com/unisocsu/chords-engine-windows/releases) ·
[**Source Code**](https://github.com/unisocsu/chords-engine-windows)

</div>


## Release v0.1.0

First public preview release: five Windows editions, including a No Model edition and installers.
