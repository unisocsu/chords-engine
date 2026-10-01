"use strict";
(() => {
  const EN = {
    "אקורדים":"ChordsEngine","ספרייה":"Library","אמנים":"Artists","אלבומים":"Albums","תיקיות":"Folders","תור נגינה":"Queue","הגדרות":"Settings","השיר הפתוח":"Open song",
    "＋ הוספת שירים":"＋ Add songs","📁 הוספת תיקייה":"📁 Add folder","גרור לכאן קבצי שמע או וידאו":"Drop audio or video files here","שם":"Name","אמן":"Artist","אלבום":"Album","משך":"Duration","סולם":"Key",
    "אקורד נוכחי":"Current chord","הבא:":"Next:","טון":"Key","קאפו":"Capo","פשוט":"Basic","רגיל":"Standard","מתקדם":"Advanced","אקורדים מעל מילים":"Chords above lyrics","אקורדים בתוך הטקסט":"Chords inline","אקורדים בלבד":"Chords only","מילים בלבד":"Lyrics only","גלילה":"Scroll",
    "✏️ עריכה":"✏️ Edit","📝 הדבקת מילים":"📝 Paste lyrics","⤓ ייצוא":"⤓ Export","העתקה ללוח":"Copy to clipboard","הדפסה / PDF":"Print / PDF","טקסט (TXT)":"Text (TXT)","אקורדים בשיר":"Chords in song","גיטרה":"Guitar","פסנתר":"Piano","מצב נגינה":"🎤 Performance mode",
    "מינימלי":"Minimal","איטי":"Slower","מהיר":"Faster","ערבוב":"Shuffle","הקודם":"Previous","נגן / עצור (רווח)":"Play / pause (Space)","עצור":"Stop","הבא":"Next","חזרה":"Repeat","מהירות":"Speed","ניקוי":"Clear",
    "▶️ חיפוש והורדת שיר":"▶️ Search & download song","🔎 חיפוש Google":"🔎 Google Search","⬇ הורד ונתח":"⬇ Download & analyze","סגירה":"Close","רמת ניתוח":"Analysis level","מודל / אוצר אקורדים":"Model / chord vocabulary",
    "🎸 רחב — Submission":"🎸 Broad — Submission","🎼 בסיסי — ISMIR 2017":"🎼 Basic — ISMIR 2017","🧠 מלא — Full":"🧠 Full",
    "הוספה לספרייה":"Add to library","תיקייה בספרייה":"Library folder","להתחיל לנתח מיד":"Analyze immediately","הוסף":"Add","ביטול":"Cancel",
    "✏️ מה לערוך?":"✏️ What do you want to edit?","בחר את סוג העריכה.":"Choose the editing mode.","מילים":"Lyrics","עריכת תמלול ושורות":"Edit transcript and lines","אקורדים":"Chords","החלפה, הוספה והזזה":"Replace, add and move","הכול":"Everything","מילים וגם אקורדים":"Lyrics and chords",
    "ערכת צבעים":"Theme","לפי המערכת":"System","בהיר":"Light","כהה":"Dark","רמת ניתוח ברירת מחדל":"Default analysis level","צבע אקורדים":"Chord color","צבע סימון":"Highlight color","גופן":"Font","מרווח שורות":"Line spacing","עדכונים":"Updates",
    "בדיקה אוטומטית לעדכונים":"Check for updates automatically","בדוק כל":"Check every","כל יום":"Daily","כל 3 ימים":"Every 3 days","פעם בשבוע":"Weekly","כל שבועיים":"Every 2 weeks","פעם בחודש":"Monthly","🔄 בדוק עכשיו":"🔄 Check now","✕ ביטול הורדה":"✕ Cancel download",
    "גרסה":"Version","מודלים":"Models","ספרייה:":"Library:","מנוע":"Engine","מודל עברית":"Hebrew model","מודל אנגלית":"English model","לא מתנגן כלום":"Nothing playing","בלי מילים":"No lyrics","לא הושלם":"Incomplete","אמן לא ידוע":"Unknown artist","בלי אלבום":"No album",
    "מצב עריכת מילים: לחץ על ✎ או לחץ פעמיים על שורה כדי לערוך את הטקסט.":"Lyrics editing mode: click ✎ or double-click a line to edit its text.",
    "מצב עריכת אקורדים: לחץ על אקורד להחלפה, גרור אותו להזזה, או לחץ במקום אחר בשורה כדי להוסיף.":"Chord editing mode: click a chord to replace it, drag it to move it, or click elsewhere on a line to add one.",
    "מצב עריכה מלא: אפשר לערוך גם מילים וגם אקורדים.":"Full editing mode: you can edit both lyrics and chords.",
    "מצב עריכה: לחיצה על אקורד — החלפה/מחיקה · לחיצה על אות — הוספת אקורד · גרירת אקורד — הזזה · לחיצה כפולה על שורה — עריכת טקסט · הכפתורים בצד השורה — הוספה/מחיקה/איחוד":"Edit mode: click a chord to replace/delete · click a letter to add a chord · drag a chord to move it · double-click a line to edit text · line buttons add/delete/merge",
    "לא זוהו אקורדים או מילים.":"No chords or lyrics were detected.","האקורדים מוכנים — אפשר לנגן. המילים בדרך…":"Chords are ready — you can play. Lyrics are coming…","ממשיך לתמלל…":"Continuing transcription…","האקורדים והמילים יופיעו כאן תוך כדי הניתוח…":"Chords and lyrics will appear here as analysis progresses…","התור ריק. ▶ או ＋ בספרייה מוסיפים שירים.":"The queue is empty. Use ▶ or ＋ in the library to add songs."
  };
  function apply(root=document.body) {
    if (document.documentElement.lang !== "en") return;
    const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT), nodes=[]; while(w.nextNode()) nodes.push(w.currentNode);
    const keys=Object.keys(EN).sort((a,b)=>b.length-a.length); for(const n of nodes){let v=n.nodeValue; for(const k of keys){if(v.includes(k)) v=v.split(k).join(EN[k]);} n.nodeValue=v;}
    root.querySelectorAll?.("[title],[placeholder],[aria-label]").forEach(el=>["title","placeholder","aria-label"].forEach(a=>{let v=el.getAttribute(a); if(v&&EN[v]) el.setAttribute(a,EN[v]); else if(v){for(const k of keys){if(v.includes(k)) v=v.split(k).join(EN[k]);} el.setAttribute(a,v);}}));
  }
  fetch("/api/config").then(r=>r.json()).then(cfg=>{
    if(cfg.ui_lang!=="en") return;
    document.documentElement.lang="en"; document.documentElement.dir="ltr"; document.title="ChordsEngine";
    apply();
    new MutationObserver(ms=>ms.forEach(m=>m.addedNodes.forEach(n=>{if(n.nodeType===1) apply(n);}))).observe(document.body,{childList:true,subtree:true});
  }).catch(()=>{});
})();