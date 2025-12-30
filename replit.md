# MetaExtract

## Overview

MetaExtract is a forensic-grade metadata extraction SaaS application that analyzes media files (images, videos, audio) to extract comprehensive hidden metadata. The application targets professionals in legal, journalism, and security fields who need to extract 7,000+ metadata fields including EXIF data, GPS coordinates, camera MakerNotes, file integrity hashes, and proprietary vendor-specific information that standard tools miss.

The platform operates on a freemium model with tiered pricing:
- **Free**: Basic images (10MB), 5 files/day
- **Starter** ($5/mo): All images + RAW formats (50MB), 50 files/day
- **Pro** ($29/mo): Images + Video + Audio (500MB), unlimited files
- **Super** ($99/mo): Hidden tier for enterprise (1GB), API access

Pay-as-you-go credits system also available for one-off extractions.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **Routing**: Wouter (lightweight client-side routing)
- **State Management**: TanStack React Query for server state
- **Styling**: Tailwind CSS v4 with custom forensic dark theme, shadcn/ui component library (New York style)
- **Animations**: Framer Motion for UI transitions and parallax effects
- **Build Tool**: Vite with custom plugins for Replit integration and OpenGraph meta tag handling

The frontend follows a component-based architecture with:
- Layout component for consistent navigation and footer
- Feature-specific components (UploadZone, PaymentModal)
- Comprehensive shadcn/ui component library for UI primitives
- Custom theming with CSS variables for a dark "cyber forensic" aesthetic

### Backend Architecture
- **Framework**: Express.js with TypeScript
- **File Processing**: Multer for multipart file uploads (500MB limit), exiftool-vendored for metadata extraction
- **API Design**: RESTful endpoints under `/api` prefix
- **Build**: esbuild for production bundling with selective dependency bundling for cold start optimization

Key backend responsibilities:
- File upload handling with memory storage
- Metadata extraction using exiftool-vendored library
- File integrity calculation (MD5, SHA256 hashes)
- Analytics logging for usage tracking
- Static file serving for production builds

### Data Storage
- **Database**: PostgreSQL via Drizzle ORM
- **Schema Location**: `shared/schema.ts` (shared between frontend and backend)
- **Migrations**: Drizzle Kit with migrations output to `./migrations`

Database tables:
- `users`: User authentication (id, username, email, password, tier, subscription info)
- `subscriptions`: Dodo Payments subscription tracking
- `extraction_analytics`: Usage tracking including tier, file type, processing time, success/failure status
- `credit_balances`: Pay-as-you-go credit balances per session/user
- `credit_transactions`: Credit purchase and usage history

### File Processing Pipeline
1. User uploads file via multipart form
2. File stored temporarily in memory (Multer)
3. exiftool-vendored extracts comprehensive metadata
4. File integrity hashes calculated (MD5, SHA256)
5. Filesystem metadata extracted (size, permissions, timestamps)
6. GPS coordinates converted to decimal format if present
7. Calculated metadata derived (aspect ratio, megapixels, file age)
8. For premium/super tiers: Python fallback enriches extraction (Pillow, mutagen, PyPDF2)
9. Response structured by tier (free users get limited fields)
10. Analytics logged to database
11. Temporary file discarded (zero-retention policy)

### Tier-Based Access Control
The application implements a freemium model where metadata fields are gated by subscription tier. Free users receive basic fields while premium tiers unlock forensic-grade data including vendor MakerNotes, complete EXIF, and extended metadata.

## External Dependencies

### Core Services
- **PostgreSQL Database**: Primary data store, connection via `DATABASE_URL` environment variable
- **exiftool-vendored**: Node.js wrapper for ExifTool, handles metadata extraction for 400+ file formats
- **Python Fallback**: For premium/super tiers, Python libraries provide enriched extraction:
  - **Pillow**: Deep image metadata (EXIF, ICC profiles, animation info)
  - **mutagen**: Audio file metadata (MP3, FLAC, OGG, M4A tags and technical info)
  - **PyPDF2**: PDF document info, page counts, encryption status

### Key NPM Packages
- **drizzle-orm / drizzle-kit**: Type-safe ORM and migration tooling
- **multer**: Multipart file upload handling
- **express-session / connect-pg-simple**: Session management with PostgreSQL backing
- **@tanstack/react-query**: Server state management
- **framer-motion**: Animation library
- **shadcn/ui ecosystem**: Radix UI primitives, class-variance-authority, tailwind-merge

### Development Tools
- **Vite**: Frontend build and dev server
- **esbuild**: Production server bundling
- **TypeScript**: Full-stack type safety
- **Replit plugins**: Dev banner, cartographer, runtime error overlay

### Implemented Integrations
- Audio metadata via mutagen (implemented in Python fallback)
- Camera vendor MakerNotes via ExifTool (implemented)
- Video metadata via ffprobe (H.264, HEVC codec details, container info)
- Extended MakerNote support for: Canon, Nikon, Sony, Fuji, Olympus, Panasonic, Pentax, Leica, Hasselblad, Phase One, Sigma, Ricoh, Casio, Minolta, Samsung, Apple, DJI, GoPro, Reconyx, Kodak, Epson, Sanyo, Kyocera

### Implemented Payment Integration
- Dodo Payments integration for subscription billing (Test Mode)
- Checkout session creation via `/api/checkout/create-session`
- Webhook handler for subscription lifecycle events at `/api/webhooks/dodo`
- Subscription status tracking in database
- **Credits System**: Pay-as-you-go credit packs (10/$2, 50/$8, 200/$25)
  - Credit costs: Standard image (1), RAW (2), Audio (2), Video (3)
  - Endpoints: `/api/credits/balance`, `/api/credits/purchase`, `/api/credits/add`
- Secrets: DODO_PAYMENTS_API_KEY, DODO_WEBHOOK_SECRET (configured)
- Product IDs configured via environment variables:
  - DODO_PRODUCT_STARTER: pdt_0NV8f7BHv56aq5nVIdg3Y
  - DODO_PRODUCT_PREMIUM: pdt_0NV8fLqUtlChurxFwXlKB

### Required Dodo Products (To Be Created)
For credits to work, create these one-time payment products in Dodo Test Mode:
- **Single Pack** ($2): Set `DODO_PRODUCT_CREDITS_SINGLE`
- **Batch Pack** ($8): Set `DODO_PRODUCT_CREDITS_BATCH`
- **Bulk Pack** ($25): Set `DODO_PRODUCT_CREDITS_BULK`

### Planned Integrations
- IPTC Core fields via iptcinfo3
- XMP metadata via python-xmp-toolkit