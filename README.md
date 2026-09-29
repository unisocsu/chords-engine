# ChordsEngine Windows

**תוכנה ל-Windows להצגת מילות שירים ואקורדים לגיטרה, עם תמלול אודיו וזיהוי אקורדים באמצעות whisper.cpp. פועלת מקומית ובאופן לא מקוון.**

**Windows software for song lyrics and guitar chords, with offline audio transcription and chord detection powered by whisper.cpp. Runs locally without requiring an internet connection.**

---

## 🇮🇱 עברית

### מה זה ChordsEngine?

**ChordsEngine Windows** היא תוכנה ל-Windows לניתוח שירים ולהפקת דף אקורדים ומילים.

התוכנה יכולה לקבל קובץ שמע, לנתח אותו באמצעות מנועי עיבוד אודיו ו-Whisper, וליצור תוצאה הכוללת:

- 🎵 מילות השיר
- 🎸 אקורדים לגיטרה
- 🎼 זיהוי סולם
- 🥁 קצב ופעמות
- 📝 הצמדת האקורדים למילים לפי זמן הנגינה
- 🔄 טרנספוזיציה
- 🎹 אצבועי גיטרה ופסנתר
- 🎛️ הצעות קאפו
- 💾 ספרייה מקומית לשירים שנותחו
- 📴 עבודה מקומית ללא צורך בחיבור לאינטרנט לאחר ההתקנה והגדרת המודל

### איך זה עובד?

ChordsEngine משלב מספר רכיבים:

- **whisper.cpp** — תמלול האודיו וזיהוי מילים וזמנים.
- **lv-chordia** — זיהוי אקורדים.
- **librosa** — ניתוח קצב ופעמות.
- **PyAV / FFmpeg** — פענוח קובצי שמע ווידאו.
- מנוע Python שמחבר את תוצאות הניתוח ומפיק דף אקורדים.

המערכת מיועדת לעבודה מקומית. עיבוד השיר מתבצע על המחשב של המשתמש.

### מהדורות Windows

בכל Build של הפרויקט נבנות חמש מהדורות:

| מהדורה | מודל Whisper | תיאור |
|---|---|---|
| **Tiny** | כלול | המהדורה הקטנה ביותר עם מודל |
| **Base** | כלול | מהדורה קלה עם מודל |
| **Small** | כלול | מודל גדול יותר לתמלול |
| **Medium** | כלול | מודל גדול יותר לאיכות תמלול גבוהה יותר |
| **No Model** | לא כלול | המשתמש בוחר קובץ מודל קיים בזמן ההתקנה |

כל מהדורה מסופקת כ-**Windows EXE Installer** ואינה דורשת התקנת Python אצל המשתמש.

### מהדורת No Model

במהדורת **No Model** המודל אינו נכלל בקובץ ההתקנה.

במהלך ההתקנה המשתמש בוחר את קובץ מודל ה-Whisper שברשותו, והמתקין מעתיק אותו לתיקיית התוכנה.

המתקין יוצר גם קיצורים:

- תפריט התחל
- שולחן העבודה

### דרישות

- Windows 64-bit
- WebView2 לצורך הממשק
- מודל Whisper מתאים למהדורה שבה משתמשים
- אין צורך ב-Python עבור גרסאות ה-EXE המוכנות

### פיתוח והרצה

למפתחים ניתן להריץ את המנוע ישירות מסביבת Python:

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

### טכנולוגיות

- Python
- whisper.cpp
- Whisper
- lv-chordia
- librosa
- PyAV
- FFmpeg
- pywebview
- WebView2

---

## 🇬🇧 English

### What is ChordsEngine?

**ChordsEngine Windows** is Windows software for analyzing songs and generating lyrics and guitar-chord sheets.

The application can process an audio file and produce results including:

- 🎵 Song lyrics
- 🎸 Guitar chords
- 🎼 Musical key detection
- 🥁 Tempo and beat information
- 📝 Time-aligned chord placement
- 🔄 Chord transposition
- 🎹 Guitar and piano fingering information
- 🎛️ Capo suggestions
- 💾 A local song library
- 📴 Offline/local processing after installation and model setup

### How does it work?

ChordsEngine combines several components:

- **whisper.cpp** — audio transcription and word/timestamp detection.
- **lv-chordia** — chord detection.
- **librosa** — tempo and beat analysis.
- **PyAV / FFmpeg** — audio and video decoding.
- A Python processing engine that combines the analysis results into a chord sheet.

The processing is designed to run locally on the user's Windows computer.

### Windows Editions

Every build produces five editions:

| Edition | Whisper model | Description |
|---|---|---|
| **Tiny** | Bundled | Smallest bundled-model edition |
| **Base** | Bundled | Lightweight bundled-model edition |
| **Small** | Bundled | Larger model for improved transcription |
| **Medium** | Bundled | Larger model for higher transcription quality |
| **No Model** | Not bundled | Choose an existing model during installation |

Every edition is distributed as a **Windows EXE Installer** and does not require Python to be installed by the end user.

### No Model Edition

The **No Model** edition does not include a Whisper model in the installer.

During installation, the user selects an existing Whisper model file. The installer copies the model into the application's installation directory.

The installer also creates shortcuts in:

- Start Menu
- Desktop

### Requirements

- Windows 64-bit
- WebView2 for the graphical interface
- A compatible Whisper model for the selected edition
- Python is not required for the packaged EXE editions

### Development

For development, the engine can be run directly from Python:

```bash
pip install -r requirements.txt
python scripts/setup_vendor.py
python -m chords_engine serve
```

Analyze an audio file:

```bash
python -m chords_engine analyze song.mp3 --out out
```

Run tests:

```bash
python -m unittest discover tests
```

### Technologies

- Python
- whisper.cpp
- Whisper
- lv-chordia
- librosa
- PyAV
- FFmpeg
- pywebview
- WebView2

---

## 🌍 Languages

The project is designed to support additional languages as development continues.

---

## 🙏 Credits

**ChordsEngine Windows** is a fork and continued development of the original chord-and-lyrics engine built with **Claude Code by [@tsoolgee](https://github.com/tsoolgee)**.

The Windows packaging, EXE editions, installers, GitHub Actions build pipeline, and continued development are maintained in this repository.

Original project attribution is intentionally preserved.

---

## 📄 License

See the project files and the licenses of the included third-party components for licensing information.
