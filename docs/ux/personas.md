Comprehensive Persona-Based UX Audit

Overview

This audit examines the MetaExtract user experience through eight distinct personas, covering both professional (B2B) and consumer (B2C) contexts. Each persona represents a realistic user type with specific motivations, technical expertise, and expectations. The analysis follows their end-to-end journey – from first discovering the product to uploading files, viewing results, and considering payment – to identify UX pain points and improvement opportunities.

Persona 1: Medical Professional (Radiologist/Doctor)

Background
• Demographics: 45-year-old radiologist (MD) with 15 years of experience.
• Tech Savvy: Moderate – uses hospital PACS systems daily but not a programmer.
• Motivation: Analyze medical imaging metadata for quality assurance, research, or patient care.
• Pain Points: Time pressure, strict privacy (HIPAA) concerns, prefers familiar medical terminology.

User Journey
• Discovery: The homepage’s forensic focus (mentions of “courts, journalists, security teams”) feels irrelevant to a doctor. There is no reference to DICOM, PACS, or medical imaging standards. This creates an expectation gap – the user expected a clinical tool, but the site looks like a generic digital forensics app.
• Upload: The user notices a “Medical” badge among supported formats but isn’t sure what it means. They upload a JPEG of an X-ray expecting extraction of medical metadata (DICOM tags, scanner info). A critical issue emerges: MetaExtract only pulls camera metadata from the photographed scan, not medical-specific data.
• Results: The user thinks, “This is just photo metadata, not medical data.” The results page shows camera settings from when the X-ray was taken (device model, exposure settings), with many advanced fields locked and no mention of patient or scan parameters. Crucially, no DICOM fields or scanner info appear at all.
• Payment: Frustration sets in – “Why pay for photo metadata?” The pricing tiers (“Professional” vs “Forensic”) don’t clarify if either unlocks actual medical metadata. There’s no indication that upgrading would reveal any clinical information, so the doctor doubts the value of paying.

Key UX Issues
• Lack of medical context: The interface assumes a forensic/photography mindset and doesn’t use medical terminology or context, leaving clinical users alienated.
• Overpromised capabilities: Marketing implies support for medical images, but in reality the tool delivers only generic photo EXIF data for a scanned X-ray – a big letdown for medical users.
• Compliance concerns: There is no visible mention of HIPAA or how patient data is handled. A doctor might worry whether uploading scans is safe and compliant.

Recommendations
• Medical-specific landing page: Provide a variant of the homepage (or content section) addressing medical imaging use cases (e.g. mention DICOM, anonymization, HIPAA compliance).
• Format detection warnings: Detect when an image is a photograph of a medical scan vs. a native DICOM file. If it’s just a photo of a scan, warn the user of limited metadata and suggest obtaining the original file if possible.
• Clinical metadata focus: If a medical format (DICOM) is uploaded, highlight clinically relevant fields (e.g. modality, scan parameters, device manufacturer) prominently in the results.
• Privacy & compliance assurances: Display HIPAA compliance badges or messages and clearly explain data handling (e.g. immediate deletion, no PHI retention) to build trust with healthcare users.

⸻

Persona 2: Investigative Journalist

Background
• Demographics: 32-year-old freelance journalist specializing in investigative reporting.
• Tech Savvy: High – comfortable with data tools (spreadsheets, OSINT) but not a developer.
• Motivation: Verify the authenticity of images or documents (e.g. spotting manipulations, identifying source) for news stories.
• Pain Points: Tight deadlines, need for credible evidence, limited budget as a freelancer.

User Journey
• Discovery: The homepage messaging about “detecting manipulation” and “extracting hidden data competitors miss” immediately resonates. It promises capabilities that align with verifying a viral photo’s origin. The journalist gets a clear value proposition that this tool could uncover clues for a story.
• Upload: “Let’s see what this protest photo contains.” They upload a downloaded social media image, expecting to find hidden info like geolocation or timestamps. The ability to queue multiple files at once is noted (useful for analyzing several images from one event). They anticipate details such as camera device info, editing history, and GPS coordinates to be revealed.
• Results: “GPS data! Camera serial number! Perfect.” The tool indeed exposes an embedded timestamp and GPS location that were not visible in a normal viewer. It also shows camera make, model, and even edit software metadata, with evidence of multiple saves (edit history) — suggesting the image might have been altered. These findings provide valuable evidence the journalist can use in their investigation.
• Payment: “This is worth it for the investigative value.” The journalist is inclined to unlock premium features after seeing the results. It’s clear that upgrading (e.g. using credits or a subscription) would yield deeper analysis like more metadata fields or tampering alerts. The pay-as-you-go credit system is appealing for a freelancer, allowing them to spend a few dollars per important investigation rather than a high recurring fee.

Key UX Issues
• Unclear feature scope: It’s not immediately obvious which advanced analysis features are behind the paywall. The journalist isn’t sure exactly what a “Forensic” tier would add (e.g. specific fields or detection capabilities).
• Batch analysis workflow: While multiple files can be uploaded, the UI doesn’t explicitly help compare or group results from related images (which would be useful for a story with many photos). The process for analyzing a set of images together is not clearly guided.
• Export options: There’s no clear way to export or download a report of the findings. For publishing or fact-check archives, the journalist might need a PDF/CSV report of the metadata, but it’s unclear how to get that.

Recommendations
• Showcase use cases: Provide example analyses relevant to journalism (e.g. a sample report from a doctored image) in documentation or marketing. This helps journalists immediately see what kind of data they can get and how it has been used to verify stories.
• Improve multi-file UX: If users upload multiple images, allow an easy way to navigate between those results or see a summary comparison. For example, enable tagging files into a “case” or side-by-side viewing of key fields (timestamps, location) to assist in storytelling.
• Enable evidence export: Add an option to export metadata results (as a report or structured data). A one-click PDF or CSV export of an image’s metadata would help journalists include it as evidence or share with editors, increasing the tool’s utility in news workflows.
• “Journalist mode”: Consider a preset view that highlights fields most relevant to verification (e.g. source camera info, dates, locations, edit history) and maybe de-emphasizes extraneous technical fields. This tailored view can speed up analysis for non-technical investigative users.

⸻

Persona 3: Law Enforcement Officer

Background
• Demographics: 38-year-old detective in a cybercrimes unit.
• Tech Savvy: Moderate – familiar with police databases and basic forensic software, but not deeply technical.
• Motivation: Extract forensic evidence from digital media (images, videos, documents) for criminal investigations.
• Pain Points: Strict chain-of-custody procedures, need court-admissible reports, bureaucratic procurement and approval processes.

User Journey
• Discovery: “This looks exactly like what we need for digital evidence.” The homepage explicitly references use cases in courts and forensic analysis. This alignment with law enforcement needs (plus phrases like “zero retention” for data) builds initial trust. The officer’s first impression is that MetaExtract is a credible forensic tool suitable for official use.
• Upload: “I need to preserve evidence integrity.” They upload a confiscated phone image. The interface shows file hash calculations (MD5/SHA256), which the officer appreciates for evidence integrity verification. Still, they remain cautious about uploading sensitive evidence to a cloud service despite the “no data retention” claim. They expect the platform to maintain a clear audit trail and not alter the file, as any changes could compromise admissibility.
• Results: “This is comprehensive, but is it court-admissible?” The tool uncovers a trove of metadata (e.g. device serial number, software versions, GPS tags) and even displays a “Chain of Custody” section with the file’s hash. While impressed with the depth, the detective isn’t sure if these results meet legal standards. There’s no note on whether the extraction method is validated or if the output can be exported in a court-friendly format. They wonder how to document these findings officially.
• Payment: “We’ll need department approval for this.” The officer sees an Enterprise tier (~$99/month) which seems designed for teams. That price is plausible for the department, but purchasing requires justification. The site does not mention any law enforcement discounts or a sales contact for enterprise licensing. The procurement process is unclear — it looks like a self-serve subscription, which might conflict with how the department typically buys software (e.g. via purchase orders or vendor contracts).

Key UX Issues
• Admissibility & compliance: The UI and docs do not mention adherence to forensic standards (like NIST guidelines or ISO certifications). There’s no clear assurance that the tool’s methods and outputs are court-admissible, which is a major concern for law enforcement.
• Chain-of-custody support: Beyond showing hashes, the platform lacks features to fully support chain of custody (e.g. logging who performed the extraction, timestamps for each action, tamper-proof reporting). Officers may need these details for legal proceedings.
• Enterprise procurement friction: The pricing and signup flow seem geared to individuals. There’s no obvious path for an agency to get volume licensing, invoicing, or to contact sales for specialized needs (e.g. on-premise deployment or higher data limits). This could stall adoption in government settings.

Recommendations
• Highlight forensic compliance: Clearly state any compliance with standards (for example, “Outputs validated against NIST DFIR standards” or “ISO 27001 certified data handling” if applicable). Even if not certified, explicitly mention that results are reproducible and that the tool uses well-known libraries (like ExifTool) which are accepted in courts.
• Chain of custody features: Introduce functionality to aid legal use, such as an audit log showing when and by whom the file was uploaded and analyzed, and an option to download a signed report (including file hashes, timestamps, and possibly a digital signature to prove the report hasn’t been altered).
• Law enforcement outreach: Provide a way for agencies to engage beyond the website – for example, a “Contact us for enterprise/government use” link. This can help with custom needs like on-prem installations or bulk purchasing. Offering paperwork like a quote or invoice instead of credit card subscription could be necessary for procurement.
• Dedicated LE mode: Consider a “law enforcement mode” that defaults to showing chain-of-custody info, hashes, and other legally pertinent metadata upfront. This mode could also automatically redact any irrelevant personal info (to prevent investigators from seeing protected data unintentionally) and ensure a professional, court-ready presentation of results.

⸻

Persona 4: Privacy-Conscious Consumer

Background
• Demographics: 28-year-old marketing professional who is very privacy-conscious.
• Tech Savvy: Moderate – active on social media and basic tech usage, but not deeply technical.
• Motivation: Check what personal data might be hidden in her photos or files before sharing them online (to avoid leaking location or other details).
• Pain Points: Distrusts apps with her personal data, finds technical jargon intimidating, and is hesitant to pay for tools unless absolutely necessary.

User Journey
• Discovery: “Finally, a way to see what’s hidden in my photos.” The homepage immediately catches her eye with promises of revealing hidden metadata. Importantly, the prominent “zero data retention” pledge and emphasis on privacy reassure her that this service won’t save her files. The free tier availability lowers the barrier – she’s willing to try it out since it costs nothing upfront.
• Upload: “Is this really safe? What happens to my photos?” Despite the assurances, she hesitates as she selects a personal vacation photo to upload. It’s a bit nerve-wracking to trust an online tool with personal images. The interface says nothing about encryption or processing location. She proceeds but remains anxious during the upload, unsure if her file might be stored or viewed by others. More explanation here about the secure processing (or a visual indicator of safe upload) could have eased her mind.
• Results: “OMG, my photo has GPS coordinates in it!” She’s surprised and alarmed by the results. The tool uncovers the exact location where the photo was taken, along with the phone model and even the software (app) used to edit it. This is an eye-opener — she had no idea her pictures carried that much info. The interface, however, is quite technical: dozens of fields with labels like “EXIF GPS Latitude” and numeric formats. It’s informative but a bit overwhelming; she only grasps some of it. Still, the key takeaway (that her camera and location were embedded) is very valuable to her.
• Payment: “The free tier was actually helpful.” After analyzing a few photos, she’s pleased that she got useful information without paying. She considers whether upgrading could help scan her entire photo library for privacy leaks. The credit system ($1 per file) and affordable monthly plans are noted, but as an occasional user, she might just stick to free or maybe buy a couple of credits. The important part is that the free experience provided real value and built enough trust that she might return.

Key UX Issues
• Trust transparency: While privacy is emphasized, the actual process is a black box to her. She’s unsure if the file is truly deleted, if it’s processed locally or on a server, etc. This lack of detailed transparency can still cause anxiety for a privacy-focused user.
• Technical intimidation: The results interface shows raw metadata fields that are hard to interpret for a layperson. The sheer volume of jargon (EXIF, XMP, etc.) could overwhelm someone just interested in a few privacy-related points.
• Lack of guidance: After seeing the metadata, there’s no guidance on what to do next. She might wonder: How do I remove this data from my photos? or What steps should I take to protect my privacy? The tool doesn’t currently provide tips or resources on addressing the findings.

Recommendations
• Explain data handling: Provide a clear, user-friendly description of what happens when a file is uploaded (e.g., “Files are processed in-memory and immediately discarded. No data is saved on our servers.”). Consider adding a small info icon or link to a privacy policy section that reassures users of the process in non-technical terms.
• Simplified results view: Offer a “basic” or privacy-focused results mode that highlights just the most important personal data findings (e.g., GPS location, device info) in simple language. For example, “This photo has location data: (New York, taken on June 5, 2023 with an iPhone 12)” and provide an option to see the full technical details if desired.
• Privacy tips: After showing the results, guide the user on next steps. This could be a short list or link: “Here’s how you can remove or edit metadata to protect your privacy…” with instructions or a link to a guide on stripping EXIF data. Educating users not only identifies the problem but also empowers them to fix it, which this persona would appreciate.
• Trust badges & UX cues: Continue emphasizing trust — perhaps add third-party privacy certifications or badges if available. Even simple UI cues like a “secure upload” icon or animation (lock icon when uploading) can reinforce that the process is safe.

⸻

Persona 5: Professional Photographer

Background
• Demographics: 35-year-old professional photographer running a freelance business.
• Tech Savvy: High – expert in using photography software (Lightroom, Photoshop) and camera gear, though not a programmer.
• Motivation: Dive deeper into EXIF and image metadata beyond what standard tools show, to verify authenticity of photos and optimize camera settings/workflow. Might also use it to check for tampering in client-delivered images.
• Pain Points: Already has workflows with Adobe Lightroom/Bridge which show basic metadata; looking for additional value. Needs integration and efficiency – exporting and managing metadata should fit into her existing process.

User Journey
• Discovery: “This might show more than Lightroom.” The marketing claims about extracting metadata that “competitors miss” intrigue her. She’s aware that Lightroom doesn’t display everything (like certain MakerNote fields specific to camera manufacturers). The tech-heavy, detailed vibe of the site appeals to her desire for granular data. She expects MetaExtract could reveal hidden camera details that standard photography tools ignore.
• Upload: “Let’s see what my camera actually records.” She uploads a RAW file from a recent shoot, anticipating a wealth of information. In particular, she’s looking for lens metadata, detailed exposure settings, color profile info, and the proprietary MakerNote data (like focus points, shutter count, or image processing settings) that aren’t visible in most apps. The upload goes smoothly, though she notices the 10MB free limit — her RAW is within that, but it reminds her that large batches might be an issue.
• Results: “Finally, the full MakerNote data!” The output confirms her hopes: she can see fields like camera firmware version, lens serial number, focus distance, and even editing software records. She also spots the history of edits (e.g., an Adobe Lightroom tag showing adjustments were made). This level of detail excites her; it’s useful for troubleshooting gear issues and verifying image authenticity. The interface is dense but she understands most of it due to her photography background. Scanning through, she mentally notes some fields she might export for her records.
• Payment: “The Professional tier looks essential for me.” Many of the specific fields (especially some MakerNote entries) are marked as locked under the free tier. She gathers that upgrading would unlock those manufacturer-specific details. At $9/month (for Professional), it seems worth it for her line of work. She also considers that a subscription might allow bulk processing of entire shoots which would be a big time saver. Overall, the pricing feels aligned with the value she would get, assuming it integrates well with her workflow.

Key UX Issues
• Unclear differentiation: It’s not obvious at first glance how MetaExtract’s output compares to using her existing tools or free utilities like ExifTool. She has to do a mental comparison to realize what extra fields she’s getting. New users might not immediately see the competitive advantage.
• Workflow integration: There’s no direct way to export the metadata results (e.g., as a sidecar file or CSV) for dozens of images or integrate with Lightroom/DAM software. Photographers often manage thousands of files; manually using the web UI for each is not feasible.
• Batch limitations: The free tier’s 10MB file limit and 10-file batch cap might be too restrictive for high-resolution RAW files or large sets. It’s unclear if the Professional tier significantly raises these limits for practical use (this information isn’t prominently shown).

Recommendations
• Competitive clarity: Provide a comparison or note in the UI/docs highlighting what MetaExtract reveals vs. common photography software. For example, “Lightroom shows ~100 metadata fields; MetaExtract can display 500+, including MakerNote details from your camera.” This helps photographers immediately grasp the value without having to upload and see for themselves.
• Metadata export: Implement an export feature for results. Even a simple “Download metadata as CSV/JSON” per file would help, but ideally allow selecting multiple files and exporting combined metadata. This would let photographers import the data into their Digital Asset Management (DAM) systems or spreadsheets for further analysis.
• Batch processing and API: If not already in higher tiers, emphasize the ability to handle large batches or provide an API. Professionals might want to script metadata extraction for an entire shoot. If the Professional or Forensic tier supports an API or higher limits, make sure that’s clear. If not, consider adding such a feature or offering a separate tool/CLI for power users.
• Photographer mode/UI tweaks: Consider a UI preset for photographers that groups metadata into logical sections (e.g., Camera Settings, Lens Info, Editing History) to save them from wading through forensic or irrelevant fields. Also, allow filtering by field type (so she could, say, show only exposure-related fields, or hide network forensic fields that don’t apply to images).

⸻

Persona 6: Corporate Security Analyst

Background
• Demographics: 42-year-old IT security analyst at a mid-sized enterprise.
• Tech Savvy: High – experienced with enterprise security tools, SIEM systems, and internal software, though not a developer.
• Motivation: Prevent data leaks and security breaches by examining files for hidden information (e.g., a document containing hidden author info or an image with location data) and verify authenticity of files (detect tampering or metadata that violates policy).
• Pain Points: Needs solutions that fit enterprise policies (SSO, user management, audit logs), must justify tools in terms of compliance and risk mitigation, and often encounters red tape in procurement.

User Journey
• Discovery: “This could help with our data leak prevention.” The website’s emphasis on metadata extraction and no data retention aligns with his data security goals. The mention of detecting manipulated content is a plus for compliance checks (e.g., verifying if an image in a report was altered). He imagines using MetaExtract to audit files for policy violations (like confidential info hidden in metadata) before they leave the company. The initial impression is positive, but he’s immediately thinking: Does this service meet our enterprise security requirements?
• Upload: “We need to analyze company documents securely.” He tests an upload with a benign corporate document image. The fact that this is a cloud service raises flags; he’s concerned about confidentiality (are the files encrypted during upload? Who can access them?). He looks for signs of enterprise-grade security (SSL is there, but what about encryption at rest or certifications?). He also wonders if there’s a way to scan many files at once (like an entire drive or dataset) as part of an audit – the single-file web upload might not scale for his needs. Nonetheless, he proceeds to see the kind of output he can get.
• Results: “The analysis is good, but where are the enterprise features?” The metadata results are detailed and reveal some hidden info (for instance, the image had an embedded username in the Author tag which could pose a privacy issue – a useful find). However, he quickly notes that there’s no user management or team collaboration features visible; it seems built for a single user. There’s also no obvious audit log of activities. If multiple analysts at his company used this, he’d want oversight of usage. The lack of SSO integration means every analyst would have separate logins – not ideal. The tool’s core functionality is solid for security analysis, but it currently feels like a consumer app, not an enterprise platform.
• Payment: “We’d need the Enterprise tier, but how do we buy this?” The pricing page shows an Enterprise plan for $99/month. The features sound relevant (maybe higher limits, better support), but the purchase flow is just a generic sign-up. There’s no option to get a formal quote or security review. He would likely need vendor paperwork, a security assessment, and to pay via invoice. None of that is evident. Without a clear enterprise sales channel or security documentation, it will be hard for him to persuade his management to adopt this tool, even if it solves a problem.

Key UX Issues
• Missing enterprise features: The app lacks obvious support for team use – no multi-user management, roles/permissions, or SSO login. There’s also no built-in audit trail of usage, which enterprises need for oversight and compliance.
• Security & compliance info: The site does not provide detail on its own security measures (certifications, encryption, data handling practices) that an enterprise infosec team would require before approving a tool. This omission can be a blocker.
• Procurement process: Enterprise purchasing is not accommodated. There’s no link to contact sales for volume or yearly licensing, no mention of SLAs or support contracts, and no option for common payment methods like purchase orders. The self-service monthly model may be too inflexible for a corporate buyer.

Recommendations
• Team and admin features: Implement an enterprise dashboard where an admin can manage multiple user accounts, view usage statistics, and enforce security policies (e.g., restrict who can upload or require certain data handling rules). Adding SSO integration (OAuth/SAML for corporate logins) would be a big plus for adoption.
• Audit logging: Provide an audit log feature that records actions (file uploaded, metadata extracted, by which user, when) accessible to enterprise admins. This log is crucial for compliance and internal investigations, ensuring the tool’s use itself can be monitored.
• Enterprise trust signals: Create a security/trust page or whitepaper for enterprise prospects. This should detail data handling (encryption in transit/at rest, retention policies), compliance certifications (GDPR, SOC 2, etc.), and perhaps client testimonials or case studies in corporate use. These signals will smooth the security review process on the customer’s side.
• Flexible procurement options: Add a “Contact Sales” or “Enterprise Inquiry” option. Offer annual billing, volume discounts, or custom agreements. Even if the pricing is $99/month by default, enterprises might want a custom plan (e.g., unlimited use for X/year with a contract). Being open to that and making it easy to initiate will reduce friction.
• Scalability for bulk use: If possible, advertise or provide a way to handle large-scale processing (maybe an API or on-premises deployment). For example, an enterprise might want to scan 10,000 files programmatically. Even if that’s a separate offering, letting the analyst know it exists (or is coming) could keep them interested.

⸻

Persona 7: Academic Researcher

Background
• Demographics: 29-year-old PhD candidate in digital forensics.
• Tech Savvy: Very high – proficient in scripting, data analysis, and using specialized forensic tools.
• Motivation: Leverage MetaExtract to study metadata patterns across large sets of files for research (e.g., analyzing how metadata varies by device or detecting novel metadata tampering techniques). Essentially using the tool as a data source for experiments.
• Pain Points: Limited budget (students have to justify every expense or find free tools), needs bulk data in a machine-readable form, and may need to modify or extend the tool’s capabilities for research purposes.

User Journey
• Discovery: “This is perfect for my metadata research project.” The sheer claim of “7,000+ hidden fields” and comprehensive format support grabs his attention. He sees MetaExtract as a treasure trove of data that could save him time instead of writing his own parsers. The open-source angle (if known to him) and forensic depth align with his academic needs. He immediately wonders if he can script against it or get large data outputs for analysis.
• Upload: “I need to analyze patterns across many files.” As a test, he uploads a couple of sample files. The process is straightforward, but he has dozens more files to go through. Doing this via the UI for each file would be tedious; he looks for an API or a bulk upload mechanism to automate the process. Also, he’s interested in the raw output (JSON/CSV) rather than the web presentation, since he plans to feed data into statistical tools or Python notebooks. The UI doesn’t clearly advertise an API, so he might have to scrape the results or find a download button (which doesn’t seem present).
• Results: “Good interface, but I really need the raw data.” The results are detailed and presented in categories, which is nice for manual inspection. He spots some interesting patterns (e.g., a field that appears in all images from a certain camera). However, extracting these findings manually is impractical. There’s no obvious “download all results” button. He might copy some JSON from the developer tools or use the browser network calls as a workaround, but this isn’t ideal. The web UI, while polished, isn’t suited for analyzing 100 files; he needs a programmatic solution.
• Payment: “Academic pricing or an open option would be great.” The free tier limits hit quickly with his larger files and need for bulk analysis. The Professional tier ($9/mo) might be sufficient in features, but even that cost can be a hurdle if he only needs it for a short-term project (and he may have to use personal funds). More importantly, the absence of an academic discount or free research license feels like a missed opportunity – many tools offer free access to academia in exchange for citations or feedback. Also, he still doesn’t see mention of an API or offline version, which are things he’d gladly pay or apply for if available.

Key UX Issues
• No API/automation support: The platform doesn’t advertise any API or command-line tool for extracting metadata, forcing heavy manual use of the UI for tasks that researchers would prefer to script.
• Data export limitations: There’s no easy way to get the metadata out in bulk (e.g. download all results as a dataset). The researcher can’t efficiently use the data in analysis tools, limiting MetaExtract’s usefulness for large-scale study.
• Cost barrier for academia: The pricing model is all commercial; there’s no mention of academic licensing, student discounts, or open-access options for research purposes. This could turn away academic users who otherwise could become advocates for the tool.

Recommendations
• Developer/API access: Provide an API or SDK for advanced users. Even if it’s a rate-limited or paid feature, having a REST API or Python library to submit files and retrieve metadata in JSON would be immensely valuable for researchers (and developers in general). This would expand MetaExtract’s use cases beyond the web interface.
• Bulk export or download: Enable users to download the results of multiple files in one go. For example, after uploading 50 files, allow a single JSON or CSV download containing all extracted metadata records. This saves researchers from manual copy-paste and opens up data mining possibilities.
• Academic program: Consider offering an academic plan or discount. This could be a verification-based free tier upgrade or a significant discount for those with .edu emails. Additionally, inviting researchers to use the tool in exchange for feedback or co-authorship in papers could be a mutually beneficial strategy. It would foster goodwill and could lead to citations in academic publications (boosting credibility).
• Open data/export formats: If possible, open-source certain aspects (if not already) or allow exporting the entire metadata schema. Researchers might want to contribute or at least understand the full list of fields MetaExtract can output. Documentation or data dumps of the fields could aid academic work and further establish MetaExtract as a reference tool in the field.

⸻

Persona 8: Tech-Curious Consumer

Background
• Demographics: 25-year-old software developer who stumbled upon MetaExtract out of curiosity.
• Tech Savvy: High – comfortable with coding and technical concepts, though not specifically knowledgeable about metadata forensics.
• Motivation: Learn about the hidden data in everyday files (images, PDFs, etc.) for personal interest and fun. Essentially treating the tool as an educational sandbox.
• Pain Points: Limited initial knowledge of metadata standards, might get overwhelmed by raw data. Wants an engaging learning experience rather than just a utilitarian tool.

User Journey
• Discovery: “Cool, let’s see what’s in my files!” The edgy, cyberpunk-themed interface actually appeals to him – it feels like a hacker tool. Seeing that it’s free to start, he’s eager to play around. The home page doesn’t scare him off with jargon; in fact, terms like “forensic metadata” pique his interest to learn more.
• Upload: “What will this show about my meme collection?” He drags in a random meme image and maybe a PDF just to see what happens. The broad format support encourages him to try various file types. He’s expecting to see a lot of technical info, which he looks forward to parsing. However, he’s also hoping the tool might help him understand the significance of that info (since he knows how to code, he could find this via Google, but a built-in explanation would be nicer). The upload and extraction process is smooth; he’s impressed by the quick turnaround.
• Results: “Fascinating! But what do all these fields mean?” The output is indeed chock-full of metadata. He sees GPS coordinates, EXIF tags, IPTC tags, file signatures, etc. It’s exciting — he had no idea all this was embedded in files. But as he scrolls, he encounters many terms he doesn’t recognize (e.g., “JUMBF” or “MakerNote” or hex values for color profiles). There are no tooltips or documentation links in the UI to explain them. Being a developer, he starts googling a few field names, but that interrupts the flow. He enjoys the discovery but wishes the app had a built-in way to learn about each field or a summary of the most interesting findings.
• Payment: “I might upgrade to explore more.” After a fun session with the free tier, he’s considering uploading more files or larger ones to see what else he can find. The concept of buying a few credits or a monthly plan isn’t a barrier for him if the curiosity continues. The free tier has successfully hooked him, showing just enough to leave him wanting more. If an upgrade promised even cooler insights (like forensic analysis or deeper fields), he’s likely to go for it later.

Key UX Issues
• Lack of educational guidance: The interface dumps raw data without context. A curious user would benefit from inline explanations (e.g., what is a MakerNote? Why is GPS data in an image?). Currently, they have to leave the app to learn these.
• Steep learning curve: The design assumes users know what to look for. Without any tutorial or guide, a novice might miss interesting patterns or not understand the significance of certain metadata.
• No onboarding/tutorial: There’s no introductory walkthrough or “did you know?” tips that might enhance the experience for first-timers. This persona is self-driven enough to explore, but a guided tour could enrich his understanding and enjoyment.

Recommendations
• Inline field explanations: Incorporate tooltips or an “info” mode where clicking on a metadata field name gives a brief description. For example, hovering over “EXIF FNumber” could show “The camera aperture value (F-stop) used when the photo was taken.” This would turn a static data dump into an interactive learning experience.
• Learning mode or highlights: Create a mode (perhaps for first-time users or enabled by a toggle) that highlights a few key metadata fields with human-readable interpretations. For instance, show a summary like “This image was taken on an Apple iPhone X on Jan 5, 2020, in Paris, France.” alongside the raw data. Storytelling with the data can draw users in and then they can dig into the raw fields if interested.
• Onboarding tour: Add a short onboarding tutorial for new users that explains the interface and what kinds of insights one can gain. This could be a series of pop-ups or a demo file analysis that points out, “Here’s where you find location info, here’s a flag that indicates editing,” etc. For a tech-savvy user, this speeds up their discovery and ensures they don’t overlook features.
• Community or docs link: Provide a link to documentation or a knowledge base for those who want to learn more. Perhaps a section of the website or a blog that explains interesting metadata stories (e.g., how certain metadata revealed a famous photo was doctored) could engage curious users and keep them on the site longer.

⸻

Cross-Persona Analysis

Common UX Issues (Across Users)
• Unclear value for non-forensic users: The core messaging and UI cater to a digital forensics mindset, which can confuse users in other domains (medical, corporate, casual consumers) about what value they’ll get. Each persona outside the forensic realm experienced some uncertainty about relevance.
• Premium features ambiguity: Many users are unsure what exactly is behind the paywall. The distinction between free vs. paid metadata (and the benefits of tiers like Professional or Forensic) isn’t clearly communicated, leading to hesitation at the upgrade step.
• Format-specific gaps: There’s a mismatch between what users expect for certain file types and what MetaExtract delivers. For example, medical users expect DICOM data but get EXIF; photographers expect easy RAW batch handling which is limited; enterprise users expect document-level metadata policy checks which aren’t explicit.
• Pricing tier semantics: The names and descriptions of tiers (“Professional”, “Forensic”, etc.) are tied to user types, not capabilities. This caused confusion – e.g., a doctor or academic isn’t sure which tier applies to them. Personas indicated a preference for feature-driven tier info (what do I get?) rather than persona-driven naming.
• Trust and security concerns: Particularly for sensitive use cases (medical, enterprise, privacy-minded users), the lack of upfront info on security, compliance, and data handling is a universal concern. Even when “zero retention” is stated, users wanted more concrete reassurance or proof.

Persona-Specific Priority Fixes
• High-Priority Personas (to address first):
• Medical Professionals – bridge the clinical context gap (ensure the product truly supports medical metadata or clearly state limitations).
• Law Enforcement – focus on evidentiary features and compliance to make the tool court-ready.
• Investigative Journalists – streamline multi-file analysis and reporting to fit their workflow and time pressures.
• Enterprise Focus:
• Corporate Security Analysts – add enterprise account management, compliance info, and bulk processing to meet corporate IT requirements.
• Academic Researchers – provide APIs or data export features, and consider academic access programs to facilitate research use.
• Consumer Education:
• Privacy-Conscious Users – maximize transparency and add guidance so they feel safe and know how to act on the info.
• Tech-Curious Users – enrich the educational aspect with explanations and tutorials to keep them engaged and learning.

Overall UX Strategy Recommendations
• Segmented experiences: Tailor landing pages or presets for different user segments. The app could detect or ask the user’s interest (e.g., “Medical”, “Photography”, “Security”) and adjust language and examples accordingly, so the value proposition is immediately clear to that user.
• Transparent feature tiers: Clearly communicate what the free tier includes and what additional data or capabilities each paid tier unlocks. Consider a preview of locked content specific to the user’s file to entice upgrades (e.g., “Upgrade to see 50 additional camera fields” or “Upgrade for DICOM tag extraction”).
• Contextual result presentation: Organize and prioritize metadata output based on use case context. For instance, show a medical user the medically relevant data first, a photographer the camera info first, etc., reducing the noise and focusing on what they care about.
• Trust-building measures: Improve communication of security and privacy practices (certifications, data deletion policies, compliance with laws). This could be done through UI elements (icons, badges) and a dedicated info page. Build features like audit logs or chain-of-custody reports to reinforce trust for professional users.
• Educational enhancements: Integrate explanations, tutorials, and perhaps community-sourced insights into the product. By helping users understand the metadata they see, MetaExtract can convert curious free users into power users and advocates. An informed user is more likely to appreciate the depth of the tool and invest in it (either financially or by promoting it).

Conclusion: This persona-based audit reveals that while MetaExtract’s core technology is powerful and comprehensive, its user experience is currently aligned mostly with expert forensic analysts. By addressing the gaps identified for each persona, the product can broaden its appeal and effectiveness — ensuring that all users, from casual individuals to professionals in specialized fields, can easily grasp its value and seamlessly integrate it into their workflows.
Appendix: Extended Persona Library

Persona 9: Builder-Founder (Pranay, MetaExtract Owner-Operator)

Background
• Demographics: 36, Bengaluru. Builder-entrepreneur shipping fast.
• Tech familiarity: Very high. Full-stack, ML-ish, product-minded.
• Motivation: Build a credible, scalable metadata platform with strong UX, clear truth boundaries, and monetization that does not feel scammy.
• Pain points: Context switching, risk of over-promising (“medical”), need for consistency across formats, balancing breadth vs. depth.

Journey
• Discovery: Not a “discoverer”. Enters from dev/test mindset. Judges conversion drop-offs by intuition first, analytics later.
• Upload: Tests many formats rapidly. Wants predictable behavior, repeatable results, deterministic schema, and fast iteration loops.
• Results: Wants:
• field coverage map (what extracted, what missing, why missing),
• stable field IDs and versioning,
• clear locking model (what is locked, why it matters),
• export + API hooks.
• Payment: Wants the paywall to be honest and defensible. No “fake scarcity”.

Key UX issues (for this persona)
• Lack of a “product truth console”: easy to accidentally claim support for medical formats when the pipeline does not.
• No “why missing” explanations: extraction gaps look like bugs.
• Locking can look like dark patterns unless previews and rationale exist.
• Hard to coordinate agents without a single canonical doc and UX principles.

Targeted recommendations
• Add an internal-facing “Coverage + Truth” panel (even hidden behind ?dev=1):
• detected format, extractor used, confidence, known limitations,
• extraction logs summary (not raw logs).
• Add schema versioning + changelog in docs.
• Create a strict “claims registry” in docs:
• allowed marketing claims by file type,
• forbidden claims until supported.

⸻

Persona 10: Curious Explorer (Generic, Not Technical)

Background
• Demographics: 30, normal internet user.
• Tech familiarity: Low to moderate.
• Motivation: “What’s hidden inside my files?” curiosity.
• Pain points: Jargon, fear of uploading private files, gets bored quickly.

Journey
• Discovery: Sees cyberpunk tone, unsure if scam.
• Upload: Tries 1 file. Wants immediate “wow”.
• Results: Needs a human summary:
• “This file reveals location”, “edited with X”, “device Y”.
• Payment: Will not pay unless the “wow” is clear and trust is high.

Key UX issues
• Raw field tables kill curiosity.
• No guided explanation of “why this matters”.

Recommendations
• Add “Highlights” card at top: 5–10 most interesting findings.
• Add definitions and “impact” labels: privacy, authenticity, provenance.
• Keep advanced tabs, but default to human summary.

⸻

Persona 11: Student (Undergrad) Working on Assignment

Background
• Demographics: 20, college student.
• Tech familiarity: Moderate.
• Motivation: Complete a digital forensics / media analysis assignment with citations.
• Pain points: Budget, needs reproducibility, needs exports, needs references.

Journey
• Discovery: Searches “metadata extractor”, lands on site.
• Upload: Uses sample files from class, expects clarity.
• Results: Needs:
• exportable JSON/CSV,
• explanation of fields,
• “how extracted” notes.
• Payment: Cannot pay or reluctant. Might use free tier heavily.

Key UX issues
• No export hurts academic workflow.
• No “method” explanation weakens credibility.

Recommendations
• Add “Academic mode”:
• citations to libraries used (ExifTool, etc.),
• “method summary” per extractor,
• free limited exports with watermark or rate-limit.

⸻

Persona 12: Student (Grad/PhD) Building Dataset or Paper

Background
• Demographics: 27, grad researcher.
• Tech familiarity: High.
• Motivation: Run extraction at scale, analyze patterns statistically.
• Pain points: Needs automation, stable schema, bulk operations.

Journey
• Upload: Bulk is the whole game. UI upload is not viable.
• Results: Wants API, batch export, field coverage metrics, repeatability.
• Payment: Will pay if programmatic workflow exists. Otherwise leaves.

Key UX issues
• Web UI is not research tooling.
• No clear field IDs, schema versions, or API docs.

Recommendations
• Provide a minimal API or CLI:
• submit file, get JSON,
• include schema version and extractor version.
• Add “bulk export” and “dataset mode” pricing.

⸻

Persona 13: OSINT / Fact-Checker (NGO or Independent)

Background
• Demographics: 34.
• Tech familiarity: High enough.
• Motivation: Verify source, time, edit history of viral media.
• Pain points: Needs defensible outputs, quick workflow, case management.

Journey
• Upload: Many files per investigation.
• Results: Needs side-by-side comparisons:
• timeline, device consistency, location consistency,
• edit tool fingerprints.
• Payment: Will pay per case.

Key UX issues
• No “case workspace”.
• No cross-file comparison view.

Recommendations
• Add “Case mode”:
• group files, compare key fields, export a case report.

⸻

Persona 14: Insurance Claims Adjuster

Background
• Demographics: 40.
• Tech familiarity: Moderate.
• Motivation: Validate photo authenticity and timeline in a claim.
• Pain points: Needs simple yes/no signals, not forensic deep dives.

Journey
• Upload: Upload 5–20 photos.
• Results: Wants:
• timestamps, GPS, edit traces,
• “risk flags” summary.
• Payment: Company pays if it reduces fraud.

Key UX issues
• Too many irrelevant fields.
• Lack of “fraud signals” summary.

Recommendations
• Add a “Risk flags” layer:
• inconsistent timestamps, missing EXIF, evidence of re-encoding/editing.
• Always show confidence and uncertainty.

⸻

Persona 15: Legal Counsel / eDiscovery Analyst

Background
• Demographics: 39.
• Tech familiarity: Moderate.
• Motivation: Evidence integrity, provenance, chain-of-custody reporting.
• Pain points: Needs auditability, exportable reports, defensibility.

Journey
• Upload: Sensitive files, wants strict privacy assurances.
• Results: Needs signed report, hashes, extraction method notes.
• Payment: Enterprise budget but procurement friction.

Key UX issues
• No formal report output.
• No clear compliance posture.

Recommendations
• Add “Court-ready report” export:
• file hashes, timestamps, extraction steps summary, tool versions.

⸻

Persona 16: Social Media Creator Checking Photos Before Posting

Background
• Demographics: 26.
• Tech familiarity: Moderate.
• Motivation: Remove location/device leaks, avoid doxxing.
• Pain points: Wants “what to fix” and “how to fix” guidance.

Journey
• Upload: Quick check before posting.
• Results: Wants:
• “You are leaking location”,
• “Remove metadata” steps.
• Payment: Might pay for batch scanning.

Key UX issues
• No remediation guidance.
• No “batch privacy scan” workflow.

Recommendations
• Add “Privacy cleanup” guidance and links to OS-level steps.
• Offer “scan a folder” feature later, but at minimum allow batch upload and a privacy score.

⸻

Persona 17: Corporate Comms / Brand Protection

Background
• Demographics: 41.
• Tech familiarity: Low to moderate.
• Motivation: Verify media used in PR is clean and authentic.
• Pain points: Needs workflow clarity and team collaboration.

Journey
• Upload: Upload marketing assets before release.
• Results: Wants:
• confirmation no location leaks,
• confirmation no weird embedded author tags,
• evidence of edit chain is known.
• Payment: Company subscription if team features exist.

Key UX issues
• UI too forensic-heavy.
• No team workflows.

Recommendations
• Add a “Brand-safe checklist” summary view.
• Later: team spaces, shared cases.

⸻

Persona 18: Archivist / Historian / Museum Digitization

Background
• Demographics: 50.
• Tech familiarity: Moderate.
• Motivation: Preserve provenance of digitized materials, document transformations.
• Pain points: Needs stable metadata exports, long-term readability.

Journey
• Upload: Scans, photos, sometimes old formats.
• Results: Wants:
• provenance notes, capture device, digitization workflow metadata,
• normalized metadata for cataloging.
• Payment: Institutional purchase.

Key UX issues
• No normalized export options.
• Too little emphasis on long-term archiving needs.

Recommendations
• Add export templates aligned to cataloging workflows.
• Add “normalization” layer: consistent keys across formats.

⸻

Persona 19: Marketplace Seller or Buyer (Authenticity)

Background
• Demographics: 29.
• Tech familiarity: Low.
• Motivation: Verify an item photo is original and not stolen or manipulated.
• Pain points: Wants a simple verdict, gets overwhelmed fast.

Journey
• Upload: Uploads listing photos.
• Results: Wants:
• “image likely re-shared”, “edited”, “metadata stripped”.
• Payment: Rarely pays. Might pay once.

Key UX issues
• Tool is too deep for them.
• Without education, they misinterpret.

Recommendations
• Add “Interpretation guardrails”: explain what metadata can and cannot prove.
• Keep “confidence” and “limitations” visible.

⸻

Persona 20: QA Engineer / SRE Debugging a Media Pipeline

Background
• Demographics: 31.
• Tech familiarity: High.
• Motivation: Find why a downstream pipeline breaks, identify format quirks.
• Pain points: Needs deterministic outputs, logs, and export.

Journey
• Upload: Many files, repeats.
• Results: Wants:
• exact parsing errors, extractor chosen, raw metadata.
• Payment: Work budget.

Key UX issues
• Missing “extraction diagnostics” view.
• No stable machine-readable output contract.

Recommendations
• Provide “Diagnostics” tab:
• extractor chain, warnings, error reasons, fallback used.

⸻

Practical product-level UX principles derived from the extended personas 1. Intent-first UX: ask or infer user intent and default to the right view (privacy, authenticity, photography, evidence, research). 2. Truth boundaries always visible: show what the tool can infer vs what it cannot, with confidence and limitations. 3. Explain missingness: “not present” and “not supported” must be distinct states. 4. Paywall must be previewable: show a concrete locked preview, not abstract promises. 5. Every persona wants export: casual users want a short report, pros want JSON/CSV, legal wants signed evidence. 6. Format-specific behavior is non-negotiable: medical is the sharpest edge here. Detect and warn early.
UX Personas Library (MetaExtract)

Path suggestion: docs/ux/personas.md

This file is the canonical persona library for MetaExtract. Use it to:
• sanity-check marketing claims and UX flows
• choose default result views and copy
• define what “success” means for each workflow

Related docs:
• docs/ux/ux-audit.md (first-principles and persona audit)
• docs/ux/agent-playbook.md (how agents turn personas into tasks)

⸻

Meta-principles (apply to every persona) 1. Intent-first UX beats feature-first UX. 2. Truth boundaries must be explicit. Never imply a capability that is not supported for the detected file type. 3. “Missing” has three distinct meanings:
• Not present in file
• Not supported by extractor
• Locked behind tier 4. Paywall must be previewable. Show exactly what unlocks for the user’s file. 5. Every persona wants export. The format differs.

⸻

Persona template (use this format when adding new ones)
• Name
• Context (B2B/B2C, environment, constraints)
• Tech familiarity
• Primary intent (privacy, authenticity, research, compliance, curiosity, workflow optimization)
• Sensitivity level (low, medium, high)
• Volume (single file, small batch, large batch, automated)
• Success criteria (what makes them say “this works”)
• Failure mode (what makes them bounce or distrust)
• UX needs (default view, copy, export, trust signals)
• Tier fit (what they should buy, if anything)

⸻

Core personas (from audit, kept short here)

P1 Medical Professional (Radiologist/Doctor)
• Intent: clinical metadata, QA, research
• Sensitivity: high
• Volume: single to small batch
• Success: sees real medical metadata (DICOM tags, modality, device), or gets a clear warning when file is just a photographed scan
• Failure: generic EXIF only, medical claims implied, no privacy/compliance clarity
• Needs: medical landing variant, format detection, “photographed scan” warning, compliance messaging, clinically relevant grouping

P2 Investigative Journalist
• Intent: provenance, authenticity, story evidence
• Sensitivity: medium
• Volume: small batch per case
• Success: finds GPS/time/edit traces, exports a report
• Failure: no export, no comparison view, unclear what paid adds
• Needs: case mode, key field highlights, exportable evidence report

P3 Law Enforcement
• Intent: evidence integrity, chain of custody
• Sensitivity: high
• Volume: case-based batches
• Success: hashes, audit trail, signed report, defensible extraction method notes
• Failure: no audit logs, unclear admissibility posture, consumer-style purchase flow
• Needs: evidence mode, chain-of-custody report, compliance/trust page, enterprise procurement path

P4 Privacy-Conscious Consumer
• Intent: remove leaks before sharing
• Sensitivity: high (personal)
• Volume: small batch
• Success: “you are leaking location/device” plus remediation steps
• Failure: jargon dump, unclear data handling, no “what to do next”
• Needs: privacy highlights, plain language, metadata removal guidance, strong trust cues

P5 Professional Photographer
• Intent: full EXIF/MakerNotes, workflow optimization
• Sensitivity: low
• Volume: large batch
• Success: sees MakerNotes and exports, batch-friendly
• Failure: no export, locked fields unclear, limits block RAW workflows
• Needs: photography mode, DAM-friendly export, batch improvements

P6 Corporate Security Analyst
• Intent: data leak prevention, compliance
• Sensitivity: high (org)
• Volume: large batch
• Success: finds hidden author/location/edit traces, audit logs, team controls
• Failure: no enterprise features, no security documentation, no procurement path
• Needs: enterprise mode, SSO/audit logs roadmap, trust page, API/bulk options

P7 Academic Researcher (PhD)
• Intent: scalable extraction, reproducible dataset
• Sensitivity: medium
• Volume: large batch, automated
• Success: stable schema, bulk export/API, method notes
• Failure: UI-only workflow, no field IDs/versioning, no bulk export
• Needs: API/CLI, schema versioning, dataset export

P8 Tech-Curious Consumer (Developer)
• Intent: exploration + learning
• Sensitivity: low
• Volume: small batch
• Success: “highlights” + tooltips + raw view
• Failure: raw tables without explanations, no onboarding
• Needs: learning mode, definitions, guided tour, interesting defaults

⸻

Extended personas

P9 Builder-Founder (Pranay, owner-operator)
• Context: building truth-first product, managing agents, avoiding over-claims
• Intent: conversion + credibility + coverage visibility
• Sensitivity: medium
• Volume: constant testing
• Success: claims registry enforced, format detection correct, lock model honest, extraction gaps explained
• Failure: accidental mis-marketing (especially “medical”), missingness ambiguity, paywall looks scammy
• Needs: internal coverage console, schema/version changelog, strict copy rules by file type

P10 Curious Explorer (Non-technical)
• Intent: “what’s hidden”
• Sensitivity: medium
• Volume: single file
• Success: quick “wow” summary
• Failure: jargon overload, feels unsafe
• Needs: highlights first, safe upload explanation, minimal UI

P11 Student (Undergrad assignment)
• Intent: complete coursework with citations
• Sensitivity: low
• Volume: small batch
• Success: export + method notes + field definitions
• Failure: no export, no reproducibility story
• Needs: academic mode, citations to libraries, report export

P12 Student (Grad/PhD dataset)
• Intent: large-scale extraction + analysis
• Sensitivity: medium
• Volume: large batch
• Success: API/CLI, stable schema IDs, bulk export
• Failure: UI-only, inconsistent fields
• Needs: programmatic access, schema versioning, bulk ops pricing

P13 OSINT / Fact-checker (NGO)
• Intent: provenance + evidence packs
• Sensitivity: medium
• Volume: case-based
• Success: compare files, timeline, export case report
• Failure: no case workspace, no comparison
• Needs: case mode, diff view, evidence report

P14 Insurance Claims Adjuster
• Intent: fraud signals
• Sensitivity: high (legal/financial)
• Volume: small to medium batch
• Success: risk flags summary + confidence
• Failure: too much noise, unclear interpretation
• Needs: risk flag layer, guardrails (“metadata is not proof”)

P15 Legal Counsel / eDiscovery Analyst
• Intent: defensible reports, chain-of-custody
• Sensitivity: high
• Volume: case-based
• Success: signed report, audit trail, tool versions, hashes
• Failure: cannot produce a court-ready artifact
• Needs: evidence report export, compliance/trust docs

P16 Social Media Creator (privacy before posting)
• Intent: prevent doxxing
• Sensitivity: high
• Volume: small batch
• Success: privacy score + fix steps
• Failure: identifies problem but gives no remediation
• Needs: privacy view + “remove metadata” guidance

P17 Corporate Comms / Brand protection
• Intent: ensure assets are clean and consistent
• Sensitivity: high (reputation)
• Volume: medium batch
• Success: checklist summary + shareable report
• Failure: forensic UI too complex for comms teams
• Needs: brand-safe checklist, simple outputs

P18 Archivist / Historian / Museum digitization
• Intent: provenance + long-term cataloging
• Sensitivity: medium
• Volume: large batch over time
• Success: normalized exports + stable keys
• Failure: no normalization, no long-term format story
• Needs: normalization layer, catalog-friendly export templates

P19 Marketplace buyer/seller (authenticity)
• Intent: quick “is this re-shared/edited”
• Sensitivity: medium
• Volume: single file
• Success: simple verdict + explanation
• Failure: overconfidence, misleading claims
• Needs: guardrails + confidence + short summary

P20 QA Engineer / SRE debugging media pipeline
• Intent: diagnose parsing issues
• Sensitivity: low
• Volume: high, repeated
• Success: diagnostics tab: extractor chain, warnings, fallbacks
• Failure: silent failures, “missing” without reason
• Needs: diagnostic view, stable machine output

⸻

Persona-to-default-view mapping

Use this to decide what the results page should default to.
• Privacy View: P4, P16, P17
• Authenticity View: P2, P13, P14, P19
• Evidence View: P3, P15
• Photography View: P5
• Medical View: P1
• Research View: P7, P12
• Learning View: P8, P10
• Diagnostics View: P20, P9

⸻

Notes on “Medical” (hard rule)

If the uploaded file is not a medical container format (DICOM/NIfTI/etc.) then:
• do not imply the tool extracted medical scan parameters
• label output as “photo metadata of a photographed scan”
• provide the “get the original file” guidance
• show exactly what is and is not possible from that input
:::

:::writing{id=“84716” variant=“standard”}

AI Agent Playbook: Persona-Driven UX Work (MetaExtract)

Path suggestion: docs/ux/agent-playbook.md

This document tells AI agents how to use personas to produce correct UX tasks, designs, and acceptance criteria. It is meant to prevent vague “improve UX” work and prevent over-claims.

⸻

1. What agents are optimizing for

Agents must optimize for:
• clarity of intent
• trust and truth boundaries
• faster time-to-first-value
• fewer dead-end clicks
• defensible paywall behavior
• predictable behavior by file type
• exportability

Agents must not optimize for:
• adding features that increase confusion
• hiding limitations
• “dark pattern” locking
• making medical promises from non-medical files

⸻

2. Required inputs for any UX task

Every task spec must reference: 1. A persona (from docs/ux/personas.md) 2. A user journey step: Discovery, Upload, Processing, Results, Paywall, Export 3. The file type reality: what metadata is actually extractable for that input 4. The missingness semantics: Not Present vs Not Supported vs Locked 5. The acceptance criteria

If any of these are missing, the task is invalid.

⸻

3. Task spec template (agents must use this exact structure)

Task Title

Short, describes user-visible outcome.

Persona and Intent
• Persona: P\_\_
• Intent: (privacy/authenticity/research/etc.)
• Sensitivity: low/medium/high
• Volume: single/small batch/large batch/automated

Problem

What fails today, with one concrete example.

Hypothesis

If we change X, then persona will achieve Y with fewer steps / higher trust.

Scope
• In scope:
• Out of scope:

UX Change

Describe the UI behavior and copy. Include default view selection.

Data/Logic Change

Describe:
• format detection rules
• extractor selection
• missingness classification rules
• lock rules

Acceptance Criteria

Bullet list of testable outcomes.
Must include:
• what the persona sees first
• what happens on wrong input type
• what the paywall previews
• export behavior (even if “not in this task”, state it)

Edge cases

At least 3.

Metrics and Instrumentation

Event names and what success looks like.

QA checklist

Manual steps an engineer can follow.

⸻

4. Persona-driven workflow: how agents choose what to build

Step A: Pick the persona and the bottleneck

Pick one persona. Identify the biggest bounce point:
• Discovery confusion
• Upload uncertainty
• Processing anxiety
• Results overload
• Paywall distrust
• Export absence

Step B: Map to default view

Use the persona-to-default-view mapping from personas.md.

Step C: Enforce truth boundaries

Before proposing copy or UI:
• confirm what fields are extractable for that file type
• if not supported, the UI must say “not supported”, not “missing”
• do not claim medical scan parameters for photographed scans

Step D: Define what to lock

Locking must be honest:
• show a preview count “unlock +N additional fields for this file”
• show examples of the actual locked fields that exist for that file
• never show “locked” for fields that do not exist in the file

Step E: Define export expectation

Every persona expects a takeaway:
• consumers: short report or shareable summary
• pros: JSON/CSV
• legal: signed PDF report
If export is not implemented, agent must propose a minimal interim: copy-to-clipboard summary or download JSON for the current file.

⸻

5. Canonical UX components agents should reuse

Agents should implement improvements by composing these reusable components.

(1) Intent Selector

A lightweight chooser on results page:
• Privacy
• Authenticity
• Photography
• Evidence
• Research
• Learning
• Diagnostics

Default selection is inferred (see Section 6).

(2) Highlights Card

Top of results:
• 5–10 items max
• plain language
• includes confidence and limitations

(3) Missingness Explainer

For any field group:
• Not present in file
• Not supported for this format
• Locked (exists, extracted, gated)
Each state has different copy and UI.

(4) Paywall Preview Panel

Shows:
• +N additional fields for this file
• the top 5 most valuable locked fields for this file
• why these matter for this persona
• clear pricing choice guidance (monthly vs credits)

(5) Export Panel

One button visible:
• Download JSON
Optional additional:
• Download CSV
• Download report PDF
For evidence/legal modes, include hashes and tool versions.

(6) Diagnostics Panel

For P20 and internal debugging:
• detected format
• extractor chain
• warnings/errors summary
• fallback used
• field group counts

⸻

6. Intent inference rules (simple, explicit)

Agents should implement deterministic inference first. Avoid ML guessing.

Examples:
• If file is RAW or has extensive EXIF/MakerNotes: default Photography View.
• If file is from social platforms or stripped metadata: default Authenticity View with “metadata stripped” highlight.
• If user arrives from “privacy” landing variant: default Privacy View.
• If user is on enterprise/evidence plan: default Evidence View.
• If user toggles Diagnostics once: remember it per user.

If uncertain, show a one-time prompt: “What are you trying to do?” with 3 choices max.

⸻

7. Hard rules for medical

Medical is the easiest place to destroy trust.

Agents must implement:
• Format detection: classify DICOM vs non-DICOM.
• If non-DICOM but image resembles scan:
• label as “photographed scan”
• explain that medical scan parameters are not embedded in this file
• suggest getting original DICOM from hospital/PACS
• Only show medical-specific groupings when the container is medical.

⸻
