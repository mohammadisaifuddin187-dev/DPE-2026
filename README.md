# DPE-2026 – Pflege-Backoffice MVP, Team 2 Materialversorgung

Semesterprojekt im Modul **Digital Process Engineering** (Prof. Dr. Volker Stiehl, THI, WS 2026/27).
Team 2 baut den Prozess **„Verbrauchsmaterial rechtzeitig nachversorgen“** und die gemeinsamen Funktionen
für Kundenfreigaben, Benachrichtigungen und Berechtigungsgrenzen.

**Lizenz:** Selbst erstellte Bestandteile stehen unter der [MIT-Lizenz](LICENSE).
**Ausgenommen** ist der Ordner `unterlagen/`. Er enthält Dokumente von Prof. Stiehl, die nicht unter MIT stehen, und muss vor einer öffentlichen Freigabe des Repos entfernt werden.

> KI-Kennzeichnung (Kursregel): Inhalte wurden mit KI-Unterstützung (Claude, Anthropic) erstellt. Der jeweilige Umfang ist in den Dateien vermerkt. Alle Inhalte werden vom Team geprüft.

## Struktur
| Pfad | Inhalt |
|---|---|
| `prozesse/team2/` | BPMN-Modelle (CIB seven / Camunda 7), Bilder, Erläuterung → [README](prozesse/team2/README.md) |
| `docs/schnittstellen/` | Schnittstellenvorschläge für den Integrationskreis |
| `docs/entscheidungen/` | Entscheidungsprotokoll |
| `werkzeuge/` | Prüfskript für Stilregeln und Label-Matching |
| `unterlagen/` | Kickoff-Unterlagen und Projektvorgaben von Prof. Stiehl (nicht MIT) |

## Stand
- [x] BPMN: Hauptprozess und 7 Teilprozesse (inkl. gemeinsamer Baustein Kundenentscheidung)
- [ ] DMN (Berechtigungsregel, Nachversorgungsbedarf, Fristen)
- [ ] External-Task-Worker, Camel-Routen (JMS, CBR), simulierter Lieferant
- [ ] Tests und teamübergreifender Beispieldurchlauf
