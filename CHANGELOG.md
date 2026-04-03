# PDFIndsigt Changelog

## v1.0.0 — 2026-04-03

### Første release
- **Enkelt PDF fane**: Drag-and-drop filvalg, metadata-træ med udfoldelige sektioner (Dokument Info, XMP, PDF Egenskaber), JSON/CSV eksport
- **Revisioner fane**: %%EOF-detektion og binær slicing af inkrementelle PDF-opdateringer, visuel tidslinje med farvede cirkler (blå=oprettet, orange=ændret, rød=metadata slettet), detaljevisning per revision
- **Mappeanalyse fane**: Parallel batch-analyse med ThreadPoolExecutor, sorterbar tabel (filnavn, sider, forfatter, dato, værktøj, revisioner, størrelse), oversigtsstatistik, CSV eksport med BOM for Excel
- **Sammenlign fane**: To-fil metadata-sammenligning med farvekodning (grøn=identisk, gul=ændret, rød=fjernet, blå=tilføjet)
- **Kerne-biblioteker**: pikepdf (XMP + revision), pypdf (Doc Info + formularer), ttkbootstrap (GUI), Pillow (billeder)
- **Dansk brugerflade**: Alle tekster på dansk via i18n/da.py
- **Mac .app bygget**: 80 MB standalone app, ingen Python nødvendig
- **Windows build-script**: build_windows.bat klar til brug
- **GitHub repo**: github.com/europalle42/pdfinsigt
