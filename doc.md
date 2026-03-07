
---

# Bachelor-CRAI Documentation

## 1. Project overview

Bachelor-CRAI is a full-stack medical imaging web application for lung CT analysis.
The system allows a user to:

* register and log in
* upload a NIfTI CT scan file (`.nii` / `.nii.gz`)
* send the file through a .NET backend
* forward the file to a Python inference service
* run an AI model for classification
* return prediction results and visualization images
* save analysis history in a database
* view earlier analyses later

The solution is split into 3 main parts:

* **Frontend**: React + TypeScript
* **Backend API**: ASP.NET Core Web API
* **Python Service**: FastAPI + PyTorch

---

## 2. High-level architecture

The application flow works like this:

1. The user logs in on the frontend.
2. The frontend stores the JWT token in `localStorage`.
3. The user uploads a CT file on the Analyze page.
4. The frontend sends the file to the .NET backend using `multipart/form-data`.
5. The backend validates the user through JWT authentication.
6. The backend forwards the file to the Python service.
7. The Python service:

   * loads the model
   * preprocesses the NIfTI volume
   * runs inference
   * creates middle-slice and Grad-CAM images
   * returns prediction data
8. The backend saves the result in SQLite.
9. The backend sends the analysis result back to the frontend.
10. The frontend shows the result page.
11. The user can later open the History page and view saved analyses.

---

## 3. Folder structure

## 3.1 Frontend

```text
frontEnd/src
├── api
│   ├── analyze.ts
│   ├── auth.ts
│   ├── client.ts
│   └── History.ts
├── App.css
├── App.tsx
├── assets
│   └── react.svg
├── components
│   ├── AnalyzeButton.tsx
│   ├── DragAndDrop.tsx
│   ├── Navbar.tsx
│   ├── Spinner.tsx
│   └── ThemeToggle.tsx
├── hooks
│   └── useTheme.ts
├── index.css
├── main.tsx
├── pages
│   ├── AnalyzePage.tsx
│   ├── HistoryPage.tsx
│   ├── HomePage.tsx
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   └── ResultsPage.tsx
└── routers
    ├── ProtectedRoute.tsx
    └── router.tsx
```

## 3.2 Backend

```text
backEnd
├── DeepLungCTApi
│   ├── Controllers
│   ├── Data
│   ├── Dtos
│   ├── Migrations
│   ├── Models
│   ├── Program.cs
│   ├── appsettings.json
│   └── deeplungct.db
└── pythonService
    ├── app.py
    ├── infer.py
    ├── model.py
    ├── checkpoints
    │   └── resnet3d_latest.pth
    └── requirements.txt
```

---

## 4. Frontend documentation

## 4.1 Purpose of the frontend

The frontend is responsible for:

* user interaction
* routing between pages
* login and registration forms
* file upload
* calling backend endpoints
* showing analysis result data
* showing saved history
* theme switching
* navigation UI

The frontend is built in **React with TypeScript**.

---

## 4.2 Entry point

### `main.tsx`

This is the starting point of the React app.

Responsibilities:

* finds the HTML root element
* creates the React root
* wraps the application in `StrictMode`
* loads the router with `RouterProvider`
* imports global styles from `index.css`

In simple terms:
`main.tsx` is what starts the frontend application.

---

## 4.3 Root layout

### `App.tsx`

`App.tsx` is the root layout component.

Responsibilities:

* renders the `Navbar`
* renders the current page through `<Outlet />`

Because routing is nested, the page content changes inside the outlet while the navbar stays visible.

---

## 4.4 Routing

### `routers/router.tsx`

This file defines all frontend routes.

Typical routes in the project:

* `/` → HomePage
* `/login` → LoginPage
* `/register` → RegisterPage
* `/analyze` → AnalyzePage
* `/results` → ResultsPage
* `/history` → HistoryPage

Protected pages are wrapped by `ProtectedRoute`.

---

### `routers/ProtectedRoute.tsx`

This file protects routes that require login.

Responsibilities:

* checks if the user is authenticated
* if authenticated, shows the page
* if not authenticated, redirects to login

This ensures that pages like Analyze and History are only available to logged-in users.

---

## 4.5 API layer

The `api` folder contains files used to communicate with the backend.

### `api/client.ts`

This file contains shared API helpers.

Typical responsibilities:

* define backend base URL
* read token from `localStorage`
* generate authorization headers
* check if the user is authenticated
* clear auth data on logout

This file is the shared utility layer for all API calls.

---

### `api/auth.ts`

This file handles authentication requests.

Responsibilities:

* send login request to backend
* send register request to backend
* store:

  * token
  * email
  * role
* update auth state in the frontend

This file is used mainly by `LoginPage` and `RegisterPage`.

---

### `api/analyze.ts`

This file sends the uploaded medical image to the backend.

Responsibilities:

* create `FormData`
* append the uploaded file
* send request to `/api/analyze`
* include JWT auth header
* return the backend response

This file is used by `AnalyzePage`.

---

### `api/History.ts`

This file handles analysis history.

Responsibilities:

* fetch list of previous analyses
* fetch one specific history item
* delete a history item if supported

This file is used by `HistoryPage`.

---

## 4.6 Hooks

### `hooks/useTheme.ts`

This custom hook manages theme switching.

Responsibilities:

* read saved theme from `localStorage`
* detect system dark/light preference
* apply `data-theme` on the HTML element
* save theme changes

This is used by the theme toggle button in the navbar.

---

## 4.7 Components

### `components/Navbar.tsx`

The navigation bar shown across the whole app.

Responsibilities:

* display logo
* show navigation links
* show login/register when user is not logged in
* show username/profile when user is logged in
* show dropdown menu with logout
* show theme toggle
* support burger menu on smaller screens

This component is important because it reflects authentication state.

---

### `components/ThemeToggle.tsx`

This component renders the theme switch button.

Responsibilities:

* show current mode
* call the toggle function from `useTheme`

---

### `components/AnalyzeButton.tsx`

A reusable button for running analysis.

Responsibilities:

* trigger analysis request
* disable itself while loading
* show spinner during analysis

---

### `components/Spinner.tsx`

A small loading indicator.

Responsibilities:

* visually show loading state
* improve feedback during login/analyze actions

---

### `components/DragAndDrop.tsx`

This component handles file selection.

Responsibilities:

* allow drag-and-drop
* allow click-to-upload
* validate selected file type
* pass the selected file back to parent page

This component is central for the Analyze page.

---

## 4.8 Pages

### `pages/HomePage.tsx`

The landing page of the application.

Responsibilities:

* explain what the system does
* give the user a starting point
* show CTA button to sign in or analyze

This page introduces the project.

---

### `pages/LoginPage.tsx`

The login page.

Responsibilities:

* show email/password form
* validate user input
* call `loginUser`
* redirect after successful login
* show error message on failure

---

### `pages/RegisterPage.tsx`

The registration page.

Responsibilities:

* show registration form
* collect email, password, confirm password, role
* validate input
* call register endpoint
* redirect after success

---

### `pages/AnalyzePage.tsx`

The page where the actual upload happens.

Responsibilities:

* let the user choose a CT scan file
* show selected file details
* trigger analysis request
* show loading state
* navigate to results page after success

This page is the bridge between UI and backend analysis flow.

---

### `pages/ResultsPage.tsx`

This page shows the analysis output.

Responsibilities:

* show predicted class
* show confidence score
* show class probabilities
* show CT middle slice image
* show Grad-CAM visualization
* show file information
* allow user to analyze another scan or view history

This is the main output page of the whole application.

---

### `pages/HistoryPage.tsx`

This page shows earlier saved analyses.

Responsibilities:

* fetch saved history from backend
* list previous records
* allow user to inspect previous results
* possibly allow delete action

This page makes the system useful beyond one single analysis.

---

## 4.9 Styling

### `index.css`

This is the main global stylesheet.

Responsibilities:

* define theme variables
* define fonts
* style navbar
* style pages and cards
* style buttons, forms, tables, badges, and result panels
* control dark/light theme colors

This file contains most of the visual design of the app.

---

### `App.css`

This file may contain extra app-specific styles, but if most styles are already in `index.css`, this file may be minimal or unused.

---

## 5. Backend (.NET API) documentation

## 5.1 Purpose of the .NET backend

The ASP.NET Core backend acts as the middle layer between frontend and Python model service.

Responsibilities:

* authenticate users
* issue JWT tokens
* receive upload requests from frontend
* forward files to Python service
* receive inference results from Python
* save analysis records in database
* return data to frontend
* provide history endpoints

It is the business-logic layer of the project.

---

## 5.2 Main backend startup

### `Program.cs`

This is the main startup file of the .NET API.

Responsibilities:

* register controllers
* register Swagger
* configure SQLite database
* configure CORS
* configure JWT authentication
* register HttpClient for Python service
* apply database migrations
* build and run the application

This file wires the backend together.

---

## 5.3 Configuration

### `appsettings.json`

This file stores application configuration values.

Typical values:

* SQLite connection string
* Python service base URL
* JWT secret
* JWT issuer
* JWT audience
* token expiry settings

This allows the backend to know where Python is running and how auth works.

---

## 5.4 Controllers

### `Controllers/AuthController.cs`

Handles authentication endpoints.

Typical endpoints:

* `POST /api/register`
* `POST /api/login`

Responsibilities:

* validate user input
* check if email already exists
* hash passwords with BCrypt
* verify passwords during login
* create JWT token
* return auth response to frontend

This controller manages user authentication.

---

### `Controllers/AnalyzeController.cs`

Handles the main analysis upload endpoint.

Typical endpoint:

* `POST /api/analyze`

Responsibilities:

* require authentication
* receive uploaded file from frontend
* validate uploaded file
* forward file to Python service
* parse Python response
* save analysis result in database
* return response to frontend

This is one of the most important files in the whole system.

---

### `Controllers/Analysishistorycontroller.cs`

Handles history-related endpoints.

Typical endpoints:

* `GET /api/history`
* `GET /api/history/{id}`
* `DELETE /api/history/{id}`

Responsibilities:

* find current authenticated user
* return only that user’s saved analysis records
* return detail for one analysis
* delete records if supported

This controller connects saved backend data to the frontend History page.

---

## 5.5 Data layer

### `Data/AppDbContext.cs`

This file defines the Entity Framework database context.

Responsibilities:

* expose `Users` table
* expose `AnalysisResults` table
* configure relations
* configure indexes
* configure EF Core mappings

This is the main connection between code and SQLite database.

---

## 5.6 DTOs

The `Dtos` folder contains Data Transfer Objects.

DTOs are used to define the shape of data sent between layers.

### `Dtos/AuthDtos.cs`

Contains request and response classes for auth.

Examples:

* `RegisterRequest`
* `LoginRequest`
* `AuthResponse`

---

### `Dtos/AnalyzeDtos.cs`

Contains DTOs for analysis-related responses.

Examples:

* Python service response DTO
* frontend/backend analysis response DTO

This helps keep JSON contracts clear.

---

### `Dtos/AnalyzeUploadRequest.cs`

Contains the upload request model.

Usually wraps:

* uploaded `IFormFile`

This makes `[FromForm]` binding cleaner.

---

## 5.7 Models

### `Models/User.cs`

Represents a user in the database.

Typical fields:

* `Id`
* `Email`
* `PasswordHash`
* `Role`
* `CreatedAtUtc`

This model is used for authentication and user ownership.

---

### `Models/Analysisresult.cs`

Represents a saved analysis result in the database.

Typical fields:

* `Id`
* `UserId`
* `UserEmail`
* `Filename`
* `ContentType`
* `SizeBytes`
* `Prediction`
* `Confidence`
* `ProbBenign`
* `ProbMalignancy`
* `SliceBase64`
* `HeatmapBase64`
* `CreatedAtUtc`

This model stores the result data returned by the Python service.

---

## 5.8 Migrations

The `Migrations` folder contains Entity Framework migration files.

Responsibilities:

* track schema changes
* create/update database tables
* keep DB structure consistent with models

These files are generated when running:

```bash
dotnet ef migrations add MigrationName
dotnet ef database update
```

---

## 5.9 Database

### `deeplungct.db`

This is the SQLite database file.

It stores:

* users
* saved analysis results

SQLite is a lightweight local database and works well for development and prototypes.

---

## 6. Python service documentation

## 6.1 Purpose of the Python service

The Python service is responsible for AI inference.

Responsibilities:

* load trained model checkpoint
* preprocess NIfTI CT input
* run classification
* generate visualization outputs
* return prediction result to backend

It is separated from .NET because the AI model is built with Python libraries such as PyTorch.

---

## 6.2 Python startup API

### `app.py`

This is the FastAPI entry point.

Responsibilities:

* create the FastAPI app
* load the model on startup
* expose `/health`
* expose `/analyze`

Typical endpoints:

* `GET /health`
* `POST /analyze`

The `/health` endpoint is useful to verify that the model service is alive and loaded.

The `/analyze` endpoint receives the uploaded NIfTI file and returns inference results.

---

## 6.3 Inference logic

### `infer.py`

This is the main inference pipeline file.

Responsibilities:

* read NIfTI bytes
* convert NIfTI to tensor
* preprocess the CT volume
* run the PyTorch model
* compute probabilities
* choose prediction class
* generate Grad-CAM
* generate middle-slice image
* return all outputs as Python dictionary

This file contains most of the AI processing logic.

---

## 6.4 Model definition

### `model.py`

This file defines the neural network architecture.

Responsibilities:

* define the 3D ResNet-style model structure
* create layers such as convolution blocks and residual blocks
* expose the final model class used by inference

The Grad-CAM logic depends on specific model layers, so this file is important for explainability output too.

---

## 6.5 Model checkpoint

### `checkpoints/resnet3d_latest.pth`

This file contains the trained model weights.

Responsibilities:

* load learned parameters into the architecture from `model.py`

Without this file, inference cannot produce real predictions.

---

## 6.6 Python dependencies

### `requirements.txt`

This file lists the Python packages required for the service.

Typical dependencies include:

* `fastapi`
* `uvicorn`
* `torch`
* `torchio`
* `SimpleITK`
* `numpy`
* `Pillow`
* `python-multipart`

These packages are needed for:

* API serving
* deep learning
* medical image reading
* preprocessing
* visualization generation

---

## 7. End-to-end request flow

## 7.1 Registration flow

1. User opens Register page.
2. Frontend sends request to backend auth endpoint.
3. Backend validates input.
4. Backend hashes password.
5. Backend saves user in SQLite.
6. Backend returns JWT token.
7. Frontend stores token and auth info.

---

## 7.2 Login flow

1. User opens Login page.
2. Frontend sends email and password.
3. Backend finds the user.
4. Backend verifies password hash.
5. Backend generates JWT token.
6. Frontend stores token in `localStorage`.
7. Navbar updates to show logged-in user.

---

## 7.3 Analyze flow

1. User opens Analyze page.
2. User uploads `.nii` or `.nii.gz` file.
3. Frontend sends file to `/api/analyze`.
4. Backend verifies JWT token.
5. Backend forwards file to Python `/analyze`.
6. Python service loads file and preprocesses it.
7. Python model predicts benign or malignancy.
8. Python generates:

   * class probabilities
   * middle slice image
   * Grad-CAM image
9. Python returns JSON to backend.
10. Backend saves result to SQLite.
11. Backend returns result to frontend.
12. Frontend opens Results page.

---

## 7.4 History flow

1. User opens History page.
2. Frontend requests `/api/history`.
3. Backend identifies user from JWT.
4. Backend returns only that user’s history.
5. Frontend displays the saved records.
6. User may open one specific result for details.

---

## 8. Authentication design

Authentication is based on JWT.

### How it works

* after login/register, backend returns a token
* frontend stores token in `localStorage`
* frontend sends token in the `Authorization` header
* backend validates token on protected endpoints

### Why JWT is used

JWT is useful because:

* it is simple for SPA frontend + API backend
* it avoids server session storage
* it works well for route protection and API authorization

---

## 9. Database design

The system mainly uses 2 entities:

### User

Represents a system user.

### AnalysisResult

Represents one saved medical scan analysis linked to a user.

### Relationship

One user can have many analysis results.

This relationship is useful because each user should only see their own analysis history.

---

## 10. Error handling

Examples of errors handled in the project:

* invalid login credentials
* duplicate registration email
* missing uploaded file
* unsupported file format
* Python service unavailable
* invalid model response
* unauthorized access to protected routes
* history item not found

Proper error handling is important so the user gets understandable feedback instead of raw crashes.

---

## 11. Styling and UI design notes

The application uses a dark clinical UI style with support for theme switching.

Main design goals:

* modern but clean look
* readable data cards
* clear result visualization
* simple auth flow
* professional medical-system feel

Typography and spacing are important because medical software should feel structured and trustworthy rather than playful.

---

## 12. Current strengths of the project

Some strengths of the current solution:

* clear separation between frontend, backend, and AI service
* modern React frontend
* dedicated .NET business/API layer
* separate Python model service for inference
* saved user-specific analysis history
* support for Grad-CAM visualization
* SQLite database makes local development simple
* JWT auth protects sensitive routes

---

## 13. Current limitations

Some current limitations of the project:

* SQLite is suitable for development, not large-scale production
* model prediction is for demonstration and not clinical use
* visualization quality can still be improved
* frontend history/details flow may still be extended
* navbar/profile system may still evolve further
* no advanced role-based dashboard yet
* no cloud deployment or distributed architecture yet

---

## 14. Future improvements

Possible future improvements:

* improve medical-style typography and UI polish
* add profile/settings page
* add more dropdown options in navbar
* add result details page/modal from history
* add pagination/filtering/search in history
* improve Grad-CAM quality and explainability
* move from SQLite to PostgreSQL/SQL Server
* add refresh token support
* add admin tools
* add audit logging
* deploy backend and Python service separately in containers
* add automated tests

---

## 15. Technologies used

### Frontend

* React
* TypeScript
* React Router
* CSS

### Backend

* ASP.NET Core Web API
* Entity Framework Core
* SQLite
* JWT Authentication
* BCrypt

### Python service

* FastAPI
* Uvicorn
* PyTorch
* TorchIO
* SimpleITK
* NumPy
* Pillow

---

## 16. Summary

Bachelor-CRAI is a multi-layer application for medical image analysis.
The frontend handles user interaction, the .NET backend handles authentication, data storage, and API logic, and the Python service handles AI inference and image visualization.

The project demonstrates how a modern web application can integrate:

* secure login
* medical file upload
* AI-based classification
* explainable visualization
* persistent user history

It is a solid foundation for a bachelor project because it combines:

* frontend development
* backend development
* database management
* authentication
* AI model integration
* medical imaging workflow concepts

---