# Code Conventions & Patterns

## TypeScript & React Conventions

- **Components**: Functional components typed with `React.FC<Props>` or standard typed props.
- **File Naming**: PascalCase for React components (`AnalysisResults.tsx`), camelCase for services and utilities (`api.ts`, `sampleImages.ts`).
- **Icons**: Sourced from `lucide-react`, instantiated as JSX components (`<Icon className="h-4 w-4" />`), never passed directly as raw child objects.
- **Styling**: Tailwind CSS utility classes organized by layout, typography, borders, and state pseudo-classes.
- **Error Boundaries**: Class-based `ErrorBoundary` in `App.tsx` preventing runtime unmounts.
- **Print Formatting**: Handled using Tailwind and `@media print` rules, with explicit `.no-print` and `.print-only` utility classes.

## Python & Backend Conventions

- **Code Style**: PEP 8 compliant, type hints on function signatures (`file_bytes: bytes, filename: str = None) -> Dict[str, Any]`).
- **Pydantic Models**: Pydantic v2 conventions using `model_config = ConfigDict(from_attributes=True)` instead of deprecated v1 `orm_mode`.
- **Async Endpoints**: FastAPI route functions declared with `async def` to support non-blocking asynchronous I/O.
- **Error Handling**: `HTTPException` with explicit status codes (400 for invalid mime types or size overflow, 500 for inference failures).

## Civil Engineering & Domain Conventions

- **Damage Severity Classification**:
  - `GRADE 1: MINOR` (Aperture < 0.3mm or no significant crack, routine monitoring)
  - `GRADE 2: MODERATE` (Aperture 0.3mm - 0.7mm, surface routing & elastomeric sealing)
  - `GRADE 3: CRITICAL` (Aperture > 0.8mm, structural evaluation, epoxy injection or CFRP)
- **Reference Standards**:
  - ACI 224R-01 (Control of Cracking in Concrete Structures)
  - ASTM C823 / ASTM C881 (Examination and Epoxy Specification)
  - AASHTO MBE / FHWA BIRM (Bridge Inspection Standards)
