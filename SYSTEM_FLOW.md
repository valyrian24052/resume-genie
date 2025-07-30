# System Flow Documentation

This document provides detailed diagrams and explanations of how the AI Resume Builder system works.

## 🔄 Complete System Flow

### Overall Architecture

```mermaid
graph TB
    subgraph "User Interfaces"
        UI1[Web Interface]
        UI2[CLI Interface]
    end
    
    subgraph "Core Application"
        RB[Resume Builder]
        YP[YAML Processor]
        LG[LaTeX Generator]
        PC[PDF Compiler]
    end
    
    subgraph "Data Layer"
        YD[YAML Data<br/>data/resume.yaml]
        LT[LaTeX Template<br/>templates/resume.tex]
    end
    
    subgraph "Output"
        PDF[Generated PDF]
        LOG[Error Logs]
    end
    
    UI1 --> RB
    UI2 --> RB
    RB --> YP
    RB --> LG
    RB --> PC
    YP --> YD
    LG --> LT
    LG --> YD
    PC --> PDF
    PC --> LOG
```

## 🌐 Web Interface Detailed Flow

### Form Submission Process

```mermaid
sequenceDiagram
    participant Browser
    participant Django
    participant Forms
    participant Views
    participant ResumeBuilder
    participant YAMLLoader
    participant LaTeXGen
    participant PDFCompiler
    participant FileSystem

    Browser->>Django: POST /generate/
    Django->>Forms: JobCustomizationForm(request.POST)
    
    alt Form Validation Fails
        Forms-->>Django: form.is_valid() = False
        Django-->>Browser: Render form with errors
    else Form Validation Passes
        Forms-->>Views: form.cleaned_data
        Views->>ResumeBuilder: ResumeBuilder()
        Views->>ResumeBuilder: load_resume()
        
        ResumeBuilder->>YAMLLoader: load data/resume.yaml
        YAMLLoader->>FileSystem: Read YAML file
        FileSystem-->>YAMLLoader: YAML content
        YAMLLoader-->>ResumeBuilder: Parsed data
        
        Views->>ResumeBuilder: generate_pdf(data, filename)
        ResumeBuilder->>LaTeXGen: generate_latex(data, template)
        LaTeXGen->>FileSystem: Read templates/resume.tex
        FileSystem-->>LaTeXGen: Template content
        LaTeXGen->>LaTeXGen: Replace {{VARIABLES}}
        LaTeXGen-->>ResumeBuilder: LaTeX content
        
        ResumeBuilder->>PDFCompiler: compile_to_pdf(latex, output_path)
        PDFCompiler->>PDFCompiler: Run latexmk command
        
        alt PDF Generation Success
            PDFCompiler-->>ResumeBuilder: Success + file path
            ResumeBuilder-->>Views: PDF file path
            Views-->>Django: Render preview.html
            Django-->>Browser: Download page
        else PDF Generation Fails
            PDFCompiler-->>ResumeBuilder: Error message
            ResumeBuilder-->>Views: Exception
            Views-->>Django: Render form with error
            Django-->>Browser: Error message
        end
    end
```

### Form Validation Details

```mermaid
flowchart TD
    A[Form Submitted] --> B{CSRF Token Valid?}
    B -->|No| C[CSRF Error]
    B -->|Yes| D{Form Fields Present?}
    
    D -->|No| E[Missing Field Error]
    D -->|Yes| F{API Key Format Valid?}
    
    F -->|Invalid| G[API Key Format Error]
    F -->|Valid| H{Job Post Not Empty?}
    
    H -->|Empty| I[Job Post Required Error]
    H -->|Valid| J[Form Valid - Proceed]
    
    C --> K[Return to Form]
    E --> K
    G --> K
    I --> K
    J --> L[Process Resume Generation]
```

## 🖥️ CLI Interface Flow

### Command Processing

```mermaid
flowchart TD
    A[CLI Command] --> B[Parse Arguments]
    B --> C{Required Args Present?}
    
    C -->|No| D[Show Usage Help]
    C -->|Yes| E[Validate Job Post File]
    
    E --> F{File Exists?}
    F -->|No| G[File Not Found Error]
    F -->|Yes| H[Read Job Post Content]
    
    H --> I[Initialize Resume Builder]
    I --> J[Load Resume Data]
    J --> K[Generate LaTeX]
    K --> L[Compile PDF]
    
    L --> M{PDF Success?}
    M -->|No| N[Show Error Message]
    M -->|Yes| O[Show Success Message]
    
    D --> P[Exit]
    G --> P
    N --> P
    O --> P
```

## 📄 Data Processing Flow

### YAML to PDF Transformation

```mermaid
graph LR
    subgraph "Input Data"
        Y[YAML File<br/>data/resume.yaml]
    end
    
    subgraph "Processing Steps"
        P1[Parse YAML]
        P2[Validate Structure]
        P3[Extract Variables]
        P4[Load Template]
        P5[Replace Variables]
        P6[Generate LaTeX]
        P7[Compile PDF]
    end
    
    subgraph "Output"
        PDF[PDF File<br/>output/resume.pdf]
    end
    
    Y --> P1
    P1 --> P2
    P2 --> P3
    P3 --> P4
    P4 --> P5
    P5 --> P6
    P6 --> P7
    P7 --> PDF
```

### Variable Replacement Process

```mermaid
sequenceDiagram
    participant YAMLData
    participant LaTeXGen
    participant Template
    participant Output

    YAMLData->>LaTeXGen: Load resume data
    LaTeXGen->>LaTeXGen: Flatten YAML to key-value pairs
    LaTeXGen->>Template: Read resume.tex
    Template-->>LaTeXGen: Template content with {{VARIABLES}}
    
    loop For each variable
        LaTeXGen->>LaTeXGen: Find {{VARIABLE}} placeholder
        LaTeXGen->>YAMLData: Get variable value
        YAMLData-->>LaTeXGen: Variable value
        LaTeXGen->>LaTeXGen: Replace {{VARIABLE}} with value
    end
    
    LaTeXGen->>Output: Final LaTeX content
```

## 🔧 Error Handling Flow

### Error Types and Handling

```mermaid
flowchart TD
    A[Operation Start] --> B{Error Occurs?}
    B -->|No| C[Success Path]
    B -->|Yes| D{Error Type?}
    
    D -->|Form Validation| E[Show Form Errors]
    D -->|File Not Found| F[Show File Error]
    D -->|YAML Parse Error| G[Show Data Error]
    D -->|LaTeX Error| H[Show Template Error]
    D -->|PDF Compilation| I[Show PDF Error]
    D -->|System Error| J[Show Generic Error]
    
    E --> K[Return to Form]
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K
    
    C --> L[Show Success]
```

### Validation Chain

```mermaid
graph TD
    A[Input Received] --> B[CSRF Validation]
    B --> C[Form Field Validation]
    C --> D[File Existence Check]
    D --> E[YAML Structure Validation]
    E --> F[Template Existence Check]
    F --> G[LaTeX Syntax Validation]
    G --> H[PDF Compilation Check]
    H --> I[Output File Validation]
    
    B -.->|Fail| Z[Error Response]
    C -.->|Fail| Z
    D -.->|Fail| Z
    E -.->|Fail| Z
    F -.->|Fail| Z
    G -.->|Fail| Z
    H -.->|Fail| Z
    I -.->|Fail| Z
    
    I -->|Success| Y[Success Response]
```

## 🏗️ Component Interaction

### Core Components Communication

```mermaid
graph TB
    subgraph "Web Layer"
        W1[Django Views]
        W2[Forms]
        W3[Templates]
    end
    
    subgraph "Application Layer"
        A1[Resume Builder]
        A2[Config Manager]
    end
    
    subgraph "Core Layer"
        C1[YAML Processor]
        C2[LaTeX Generator]
        C3[PDF Compiler]
    end
    
    subgraph "Data Layer"
        D1[YAML Files]
        D2[LaTeX Templates]
        D3[Output Files]
    end
    
    W1 <--> A1
    W2 <--> W1
    W3 <--> W1
    A1 <--> A2
    A1 <--> C1
    A1 <--> C2
    A1 <--> C3
    C1 <--> D1
    C2 <--> D2
    C3 <--> D3
```

## 📊 Performance Flow

### Processing Time Breakdown

```mermaid
gantt
    title Resume Generation Timeline
    dateFormat X
    axisFormat %s
    
    section Form Processing
    Form Validation    :0, 100
    
    section Data Loading
    YAML Loading       :100, 200
    Template Loading   :150, 250
    
    section Generation
    Variable Replace   :250, 400
    LaTeX Generation   :400, 500
    
    section Compilation
    PDF Compilation    :500, 2000
    File Validation    :2000, 2100
    
    section Response
    Response Prep      :2100, 2200
```

## 🔄 State Management

### Application State Flow

```mermaid
stateDiagram-v2
    [*] --> FormDisplay
    FormDisplay --> FormSubmitted : User clicks Generate
    FormSubmitted --> Validating : Process form
    
    Validating --> FormDisplay : Validation fails
    Validating --> Processing : Validation passes
    
    Processing --> LoadingData : Start generation
    LoadingData --> GeneratingLaTeX : Data loaded
    GeneratingLaTeX --> CompilingPDF : LaTeX ready
    CompilingPDF --> Success : PDF created
    CompilingPDF --> Error : Compilation fails
    
    Success --> DownloadReady : Show preview
    Error --> FormDisplay : Show error
    DownloadReady --> [*] : User downloads
```

This documentation provides a comprehensive view of how the AI Resume Builder system processes requests, handles data, and generates PDFs. Each diagram shows different aspects of the system flow, from high-level architecture to detailed error handling.