# TenderAnalyzer Frontend

Modern Next.js frontend for the TenderAnalyzer AI-powered tender analysis platform.

## 🚀 Tech Stack

- **Next.js 16** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS 4** - Styling
- **Shadcn/UI** - UI components
- **React Query (TanStack Query)** - Server state management
- **Recharts** - Data visualization
- **Zustand** - Client state management
- **React Dropzone** - File uploads
- **EventSource API** - SSE for real-time updates

## 📦 Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local

# Edit .env.local and set:
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🏃 Development

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

The application will be available at [http://localhost:3000](http://localhost:3000)

## 🏗️ Project Structure

```
frontend/
├── app/
│   ├── page.tsx                          # Homepage with tender upload
│   ├── layout.tsx                         # Root layout with providers
│   ├── providers.tsx                      # React Query provider
│   └── tenders/
│       └── [tenderId]/
│           ├── upload/page.tsx            # Proposal upload
│           └── analysis/page.tsx          # Analysis & results
├── components/
│   ├── analysis/
│   │   ├── AnalysisDashboard.tsx         # Main dashboard
│   │   ├── ScoreCard.tsx                 # Proposal score cards
│   │   └── FindingsTable.tsx             # Findings table
│   ├── charts/
│   │   ├── RadarScoreChart.tsx           # Radar chart for scores
│   │   ├── BudgetComparisonChart.tsx     # Budget bar chart
│   │   └── FindingsPieChart.tsx          # Findings distribution
│   ├── tenders/
│   │   ├── TenderUploadZone.tsx          # Drag & drop upload
│   │   └── ProposalUploadForm.tsx        # Multi-step form
│   ├── layout/
│   │   └── AnalysisProgressIndicator.tsx # SSE progress indicator
│   └── ui/                                # Shadcn components
├── hooks/
│   ├── useAnalysis.ts                     # Analysis operations
│   ├── useTender.ts                       # Tender operations
│   └── useSSEStream.ts                    # SSE streaming
├── lib/
│   ├── api.ts                             # API client
│   ├── types.ts                           # TypeScript types
│   ├── utils.ts                           # Utility functions
│   ├── helpers.ts                         # Helper functions
│   └── chart-utils.ts                     # Chart transformations
└── package.json
```

## 🎯 Features

### 1. Tender Upload
- Drag & drop PDF upload
- File validation (type, size)
- Upload progress indicator
- Auto-redirect to proposal upload

### 2. Proposal Upload
- Multi-step form (Info → Principal → Attachments)
- Multiple proposal support
- File management
- Visual progress tracking

### 3. Real-time Analysis
- SSE connection for live updates
- Progress bar with percentage
- Step-by-step status messages
- Automatic report display on completion

### 4. Analysis Dashboard
- Executive summary
- Proposal comparison cards
- Interactive charts:
  - Radar chart for score breakdown
  - Bar chart for budget comparison
  - Pie chart for findings distribution
- Filterable findings table
- Comparison matrix

## 🔌 API Integration

The frontend communicates with the FastAPI backend via:

### REST Endpoints
- `POST /tenders/upload` - Upload tender PDF
- `POST /proposals/upload/{tender_id}/{contractor_id}/{company_name}` - Upload proposal
- `POST /tenders/{tender_id}/analyze` - Start analysis
- `GET /get-analysis-report` - Get analysis results
- `GET /tenders/{tender_id}/analysis/status` - Get analysis status

### Server-Sent Events (SSE)
- `GET /sse/stream` - Real-time analysis updates

## 📊 Data Flow

1. **Upload Tender** → Backend extracts text
2. **Upload Proposals** → Backend organizes files
3. **Start Analysis** → LangGraph agents process in background
4. **SSE Updates** → Frontend receives progress events
5. **Display Results** → Dashboard shows comprehensive analysis

## 🎨 Component Architecture

### Page Flow
```
HomePage
  ↓
TenderUploadZone
  ↓
ProposalUploadPage
  ↓
ProposalUploadForm (multi-step)
  ↓
AnalysisPage
  ├─ AnalysisProgressIndicator (SSE)
  └─ AnalysisDashboard
      ├─ ScoreCard (multiple)
      ├─ RadarScoreChart
      ├─ BudgetComparisonChart
      ├─ FindingsPieChart
      └─ FindingsTable
```

### State Management
- **Server State**: React Query for API calls and caching
- **Client State**: React hooks for local UI state
- **Real-time**: SSE for analysis progress

## 🛠️ Development Tips

### Adding New Components
```bash
# Add Shadcn components
npx shadcn@latest add [component-name]
```

### Type Safety
All API responses are typed in `lib/types.ts`. Update types when backend contract changes.

### Styling
- Use Tailwind utility classes
- Use Shadcn components for consistent UI
- Colors follow defined palette in `chart-utils.ts`

## 🐛 Troubleshooting

### CORS Issues
Ensure backend has CORS configured for frontend URL:
```python
# In backend main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### SSE Connection
If SSE doesn't connect, check:
1. Backend is running on correct port
2. `NEXT_PUBLIC_API_URL` is set correctly
3. Browser console for connection errors

### Build Errors
```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

## 📝 License

MIT
