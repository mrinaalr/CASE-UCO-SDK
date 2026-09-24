# Machines, v0.0.2

v0.0.2 corrects four dates and adds Matson's federal charge. Adepoju's interval ends on 2018-03-29, the last day the indictment states. Obaseki's business-email-compromise layer is in or around September 2019, a month. Matson's romance interval starts on 2020-02-08, the earliest day stated. Taylor's 2018-01-01 and 2025-07-31 instants stay, and each description says the instrument gave a bound, not that calendar day. Matson's Count 1 is 18 U.S.C. § 1349, asserted in the indictment. This is not a new corpus.

v0.0.0 is the local commit `b144fc4` (the validated slice). v0.0.1 dates steps the charging instruments already contained and were collapsed into one window. It does not add a new corpus. The fraud-wide set of 71 sentencing filings, 33 pleas, and 11 factual bases is not a set of later filings on these sixteen dockets. On disk, only Augustine has a plea agreement and sentencing memoranda for this docket. A plea filed as E.D. Va. 1:25-cr-46 is Eleview International, an export-control case, and is not Hunt's E.D. Mo. 1:25-cr-00046 indictment.

Occupancies are allegations. Confidence `55` means "this public instrument says so." It is not a verdict.

Each close-read graph validates with the trajectories extension, the legal-process extension, and time and PROV-O profiles. Adepoju, Cofer, Matson, and Obaseki also load the layered extension. Palafox, the pig-butchering complaint, and Stormgain also load the cryptocurrency extension. Askarkhodjaev also loads the RICO extension. Strict concepts and RDFS inference are on. The directory holds eighteen close-read Turtle files: sixteen from court instruments and two phase-label graphs, `production-2251.ttl` and `enticement-2422.ttl`. Four keyword graphs live under `recap/` and are not part of that eighteen. The eighteen were revalidated for v0.0.2 and conform, with zero violations.

A local critic pass (model calls off, so no court text left the machine) accepted the SHACL results and flagged relationship labels such as `operates`, `located-in`, and `Member_Of`. Those labels stay. The UCO relationship list is for observables (`Contained_Within`, `Sent_By`, and the like). These edges connect people, organizations, and places, and the description on each edge says which paragraph it comes from.

## Fraud study bench

| Graph | Case | What the tech does |
| --- | --- | --- |
| `alcedo-english-course.ttl` | Alcedo Mendoza, S.D. Fla. 1:21-cr-20328, doc 438504917 | Telephone, script, FedEx, payment card. Counts 2–18 date packages, calls from Peru, and payments from November 2016 through June 2017. |
| `augustine-inheritance.ttl` | Augustine et al., S.D. Fla. 1:24-cr-20140, doc 449969604 | Purchased lists, mail, then email and phone. Counts 2–22 date the letters and the calls. Akhimie's plea agreement and two sentencing memoranda are on the docket; the proffer attachment was not readable. |
| `cofer-insider-account.ttl` | Cofer, S.D. Fla. 9:20-mj-08273, doc 141451183 | Care access, then client accounts, an add-on card, and a recruited debit card. |
| `adepoju-phishing-w2.ttl` | Adepoju, N.D. Ill. 1:21-cr-630, doc 442720807 | Executive-impersonation email. Dating sites supply mule accounts. Through ¶12. |
| `odus-bec-laundering.ttl` | Odus, N.D. Ga. 1:18-cr-492, doc 385303248 | Sham account receives business-email-compromise wires and converts them. Five dated episodes in 2018. The graph contains dollar amounts and does not contain account numbers. |
| `obaseki-multi-scheme.ttl` | Obaseki, E.D. Tex. 4:21-cr-253, doc 217799634 | Three concurrent layers: romance, business-email compromise, unemployment deposits. |
| `hunt-ppp-portal.ttl` | Hunt, E.D. Mo. 1:25-cr-46, doc 432127749 | False PPP application through a lender portal on 2021-04-30. Lookup name says Patel. PDF says Hunt. |
| `matson-romance-recruiter.ttl` | Matson, E.D. Mo. 4:21-cr-654, doc 186541465 | Charging instrument and a federal charge, 18 U.S.C. § 1349. Romance mail, a postal warning, then the same story used on other people. Overt acts date $20,000, $50,000, and $125,000 inbound, then a mailing to Minnesota. |

Castanos Garcia is the elder-fraud exemplar. It is not rebuilt here.

## Benefit-at-expense test

Every close read carries `traj:BenefitAnatomy` and `traj:ExploitationAssessment` (trajectories v0.5.0). The offense name is not an input. The test passes only when an identified person supplies the gain, does not keep it, and the instrument alleges deception, coercion, or vulnerability. The gain is a preexisting thing of theirs, their activity, or use of them, including a product made from that use. A preexisting object also passes the narrower extraction test. Activity and use pass the expense test and fail that object test. `exploitationOnset` is the interval of the goal edge's arriving phase, and only on a pass. Where the instrument still gives only one window, the onset is that window. Rojas now starts the labor phase on 2021-12-22, the day the first worker was told the labor was required. Matson's recruiter onset is the May–September 2020 recruit window; the transfer dates sit on the actions. A false result is not a finding that the conduct was lawful. Keyword graphs are not assessed.

Use of a minor is proved two ways. The synthetic exemplar passes a product made from a minor and rejects a minor who is not the source, use with no alleged defect, and benefit from absence. Two primitive CaseLinker phase graphs, read under NHSR 7768, are scored here without copying names or phase comments: `production-2251.ttl` and `enticement-2422.ttl`. The CAC class name ExploitationPhase is not an input. The withheld court folder in this workbench is still not read.

| Trajectory | Expense test | Why |
| --- | --- | --- |
| Alcedo scheme | passes, object | Card payment is the consumer's money, taken by deception. |
| Augustine scheme | passes, object | Advance fee in the paragraphs read through ¶9. |
| Cofer account takeover | passes, object | Client funds spent and deposited. |
| Cofer recruited account | passes, object | Client funds moved through the recruited account. |
| Adepoju phishing | passes, object | W-2 or wire, then a filing or onward transfer. |
| Adepoju romance-mule | withheld | The ask is alleged. No terminal occupancy. |
| Odus proceeds | passes, object | The payer's wire is received and converted. |
| Hunt portal | fails | The application is false. The supplier is the lending program, not an identified person. |
| Obaseki romance | withheld | No completed transfer in the portion read. |
| Obaseki BEC | not realized | The institution blocked the transfer. |
| Obaseki unemployment insurance | withheld | Deposits are described. No terminal occupancy. |
| Matson romance target | passes, object | Currency was mailed before the postal warning. |
| Matson recruiter | passes, object | Overt acts allege the later funders' transfers were completed, then mailed onward. September 2020 requests are not asserted as paid. |
| Palafox | passes, object | Investor funds diverted after a false trading pitch. |
| Gugnin | fails | Completed bank access. The gain is not a person's property or work. |
| Pig-butchering forfeiture | passes, object | Cryptocurrency the person sent, then lockout. Civil complaint. |
| Stormgain | fails | The endpoint is the wallet link. No withdrawal is stated. Civil complaint. |
| Rojas | passes, activity | Unpaid domestic labor. The object test fails. |
| Gonzalez | passes, activity | Panhandling under threat. Identification is the means, not the goal. |
| Askarkhodjaev | passes, object | Visa fee. Placement is not scored as labor. Partial read. |
| Taylor | passes, activity | Unpaid required labor. The object test fails. |

## Methodology test

Same method, other crime types. Not the fraud study.

| Graph | Instrument | Pathway |
| --- | --- | --- |
| `palafox-bitcoin-mlm.ttl` | Indictment, E.D. Va. 1:25-cr-52, doc 437269300 | Promoter network, false bitcoin-trading pitch, portal, funds paid to other investors. Dec 2019–Oct 2021. Count 14 dates a $200,000 concealment wire on 2021-09-24. Account numbers are not recorded. |
| `gugnin-evita-payments.ttl` | Indictment, E.D.N.Y. 1:25-cr-191, doc 442161436 | Payments firm, false statements to banks, masked routing. Overview only. |
| `pigbutcher-usdt-forfeiture.ttl` | Civil forfeiture complaint, E.D. Mich. 2:25-cv-13121, doc 454395974 | Message, relationship, fake app, lockout. The complaint's typical sequence, not a dated conspiracy. |
| `stormgain-wallet-backdoor.ttl` | Civil forfeiture complaint, S.D. Ga. 4:24-cv-26, doc 385173671 | Buyer persona on WhatsApp, trading app, wallet linked to a smart contract. |
| `rojas-domestic-labor.ttl` | Indictment, C.D. Cal. 2:25-cr-110, doc 458211891 | Recruit, house, unpaid domestic labor, debt and documents, outside job. Overt acts date four adult workers from 2021-12-22 through 2023-10-28. The defendants' child is not described. |
| `gonzalez-ivm-labor.ttl` | Indictment, S.D. Cal. 3:19-cr-03255, doc 111384977 | Recruit, panhandling under threat, identification taken. Manner ¶¶38–40. |
| `askarkhodjaev-visa-labor.ttl` | Superseding indictment, W.D. Mo. 4:09-cr-00143, doc 6053810 | Labor leasing, fraudulent visas, recruitment fees, unauthorized placement. Partial. 126 pages. |
| `taylor-call-center-labor.ttl` | Superseding indictment, E.D. Mich. 2:25-cr-20560, doc 488069557 | Recruit, call quota, unpaid labor. Other allegations in that indictment are not states. |
| `production-2251.ttl` | CaseLinker phase graph, D.D.C. 1:22-cr-00150, § 2251(a), (e). NHSR 7768 | Passes at the recording, on coercion. Targeting and the coercion messages are earlier and are not the onset. |
| `enticement-2422.ttl` | CaseLinker phase graph, D.D.C. 1:23-cr-00064, § 2422(b). NHSR 7768 | Passes when material is retained, on vulnerability. The machine says that edge has no explicit threat. Contact is not the onset. |

Keyword graphs, which are an index and not a chronology, are in `recap/`.

## What v0.0.1 did not turn into a timeline

Askarkhodjaev is still a partial read of a 126-page indictment. Taylor's internal texts are not states. Adepoju's unreadable year tokens were not guessed. Cofer, Obaseki, Gugnin, Gonzalez, the pig-butchering complaint, and Stormgain stay at the prior slice. No withheld or sealed PDF was read. The two phase-label graphs were not re-read from court PDFs.
