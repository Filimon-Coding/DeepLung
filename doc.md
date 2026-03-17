
---

# Bachelor-CRAI Documentation

## 1. Project overview

Bachelor-CRAI is a full-stack medical imaging web application for lung CT analysis.
The system allows clinical staff (doctors, nurses, radiologists) to:

* request access — a form sent to the administrator
* log in with a system-generated user ID and temporary password
* change their password on first login
* upload a NIfTI CT scan file (`.nii` / `.nii.gz`)
* send the file through a .NET backend
* forward the file to a Python inference service
* run an AI model for classification
* return prediction results and visualization images
* save analysis history in a database
* view earlier analyses later

Administrators can:

* review incoming access requests from staff
* approve requests and auto-generate user IDs and temporary passwords
* reject requests
* view, edit, and delete user accounts (e.g. when an employee leaves)
* reset a user's password

The solution is split into 3 main parts:

* **Frontend**: React + TypeScript
* **Backend API**: ASP.NET Core Web API
* **Python Service**: FastAPI + PyTorch

---

## 2. High-level architecture

The application flow works like this:

1. A staff member (e.g. a doctor) fills in the access request form with their name, personnummer, mobile number, email, and position.
2. The admin receives the request in the admin panel.
3. The admin approves the request. The system generates a unique user ID (e.g. `yobe2801`) and a temporary password.
4. The admin copies and sends the credentials to the staff member.
5. The staff member logs in with their user ID and temporary password.
6. On first login, the system redirects the user to change their password.
7. The user uploads a CT file on the Analyze page.
8. The frontend sends the file to the .NET backend using `multipart/form-data`.
9. The backend validates the user through JWT authentication.
10. The backend forwards the file to the Python service.
11. The Python service:

    * loads the model
    * preprocesses the NIfTI volume
    * runs inference
    * creates middle-slice and Grad-CAM images
    * returns prediction data
12. The backend saves the result in SQLite.
13. The backend sends the analysis result back to the frontend.
14. The frontend shows the result page.
15. The user can later open the History page and view saved analyses.

---

## 3. Folder structure

## 3.1 Frontend

```text
frontEnd/src
├── api
│   ├── admin.ts
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
│   ├── admin
│   │   ├── AccessRequestsPage.tsx
│   │   ├── AdminDashboard.tsx
│   │   └── UsersPage.tsx
│   ├── AnalyzePage.tsx
│   ├── ChangePasswordPage.tsx
│   ├── HistoryPage.tsx
│   ├── HomePage.tsx
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   └── ResultsPage.tsx
├── routers
│   ├── AdminRoute.tsx
│   ├── ProtectedRoute.tsx
│   └── router.tsx
└── utils
    └── userId.ts
```

## 3.2 Backend

```text
backEnd
├── DeepLungCTApi
│   ├── Controllers
│   │   ├── AccessRequestsController.cs
│   │   ├── AdminController.cs
│   │   ├── AnalyzeController.cs
│   │   ├── AnalysisHistoryController.cs
│   │   └── AuthController.cs
│   ├── Data
│   │   └── AppDbContext.cs
│   ├── Dtos
│   │   ├── AuthDtos.cs
│   │   ├── AnalyzeDtos.cs
│   │   └── AnalyzeUploadRequest.cs
│   ├── Migrations
│   ├── Models
│   │   ├── AccessRequest.cs
│   │   ├── AnalysisResult.cs
│   │   └── User.cs
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
* routing between pages (including admin-only pages)
* login and access request forms
* first-login password change
* file upload
* calling backend endpoints
* showing analysis result data
* showing saved history
* theme switching
* navigation UI with role-aware links

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

Routes in the project:

* `/` → HomePage
* `/login` → LoginPage
* `/register` → RegisterPage (access request form)
* `/change-password` → ChangePasswordPage
* `/analyze` → AnalyzePage *(protected)*
* `/results` → ResultsPage *(protected)*
* `/history` → HistoryPage *(protected)*
* `/admin` → AdminDashboard *(admin only)*
* `/admin/requests` → AccessRequestsPage *(admin only)*
* `/admin/users` → UsersPage *(admin only)*

---

### `routers/ProtectedRoute.tsx`

Protects routes that require any authenticated user.

Responsibilities:

* checks if the user has a valid JWT token
* if authenticated, shows the page
* if not authenticated, redirects to `/login`

---

### `routers/AdminRoute.tsx`

Protects routes that require admin role.

Responsibilities:

* checks if the user is authenticated
* checks if `role === "admin"` in `localStorage`
* if both pass, shows the admin page
* if not authenticated, redirects to `/login`
* if authenticated but not admin, redirects to `/analyze`

---

## 4.5 API layer

### `api/client.ts`

Shared API helpers.

Responsibilities:

* define backend base URL
* read token from `localStorage`
* generate authorization headers
* check if the user is authenticated
* clear auth data on logout

---

### `api/auth.ts`

Handles authentication requests.

Responsibilities:

* send login request to backend (using userId + password)
* store JWT token, userId, role, and `mustChangePassword` flag in `localStorage`
* fire `auth-changed` event so the navbar updates immediately

---

### `api/admin.ts`

Handles all admin-related requests.

Responsibilities:

* submit access request (public — no auth required)
* fetch all access requests (admin only)
* approve a request — sends generated userId and temp password to backend
* reject a request
* fetch all users (admin only)
* update a user's details (admin only)
* delete a user account (admin only)
* reset a user's password (admin only)

Types exposed:

* `AccessRequest` — shape of a staff access request
* `AdminUser` — shape of a user as seen by admin
* `CreatedUser` — response after approving a request

---

### `api/analyze.ts`

Sends the uploaded medical image to the backend.

Responsibilities:

* create `FormData`
* append the uploaded file
* send request to `/api/analyze`
* include JWT auth header
* return the backend response

---

### `api/History.ts`

Handles analysis history.

Responsibilities:

* fetch list of previous analyses
* fetch one specific history item
* delete a history item

---

## 4.6 Utilities

### `utils/userId.ts`

Contains helper functions for generating user credentials.

#### `generateUserId(firstName, lastName, personnummer, existingIds)`

Builds a unique user ID from:

* 2 first letters of first name (lowercase)
* 2 first letters of last name (lowercase)
* 2-digit birth day extracted from the Norwegian personnummer (DDMMYY format)
* 2-digit counter starting at `01`, incremented only if the prefix already exists

**Example:**
Ben Ten, personnummer starting with `28` (born 28th) → `bete2801`
Tor Eide, personnummer starting with `20` (born 20th) → `toei2001`

The counter only increases if there is a conflict — i.e. if another user with the same prefix already exists.

#### `generateTempPassword()`

Generates a random 10-character temporary password.
Excludes visually ambiguous characters such as `0`, `O`, `1`, `l`, and `I`.

---

## 4.7 Hooks

### `hooks/useTheme.ts`

Custom hook that manages theme switching.

Responsibilities:

* read saved theme from `localStorage`
* detect system dark/light preference
* apply `data-theme` on the HTML element
* save theme changes

---

## 4.8 Components

### `components/Navbar.tsx`

The navigation bar shown across the whole app.

Responsibilities:

* display logo
* show navigation links: Home, Analyze, History
* show **Dashboard** link only when logged in as admin
* show Login when user is not logged in
* show user ID in profile button when logged in
* show profile dropdown with **Change password** and **Logout**
* support burger menu on smaller screens
* sync auth state on `auth-changed` events and route changes

The navbar reads `userId` and `role` from `localStorage` so it always reflects the current session.

---

### `components/ThemeToggle.tsx`

Renders the light/dark mode toggle button.

---

### `components/AnalyzeButton.tsx`

A reusable button for running analysis.

Responsibilities:

* trigger analysis request
* disable itself while loading
* show spinner during analysis

---

### `components/Spinner.tsx`

A small loading indicator used during loading states.

---

### `components/DragAndDrop.tsx`

Handles file selection for CT upload.

Responsibilities:

* allow drag-and-drop
* allow click-to-upload
* validate selected file type
* pass the selected file back to parent page

---

## 4.9 Pages

### `pages/HomePage.tsx`

The landing page. Introduces the system and gives CTA buttons to sign in or analyze.

---

### `pages/LoginPage.tsx`

The login page.

Responsibilities:

* show user ID and password form
* validate input
* call login endpoint
* if `mustChangePassword` is true, redirect to `/change-password`
* otherwise redirect to `/analyze`
* show error message on failure

---

### `pages/RegisterPage.tsx`

The access request form. Staff no longer register themselves — they submit a request which the admin reviews.

Responsibilities:

* collect first name, last name, personnummer (11-digit Norwegian format), mobile number, private email, and position/role
* validate personnummer length
* submit to `POST /api/access-requests`
* show success message with instructions to wait for admin

---

### `pages/ChangePasswordPage.tsx`

Shown on first login when `mustChangePassword` is true.

Responsibilities:

* show current password, new password, and confirm new password fields
* validate that new passwords match
* call change-password endpoint
* on success, clear `mustChangePassword` flag and redirect to analyze

---

### `pages/AnalyzePage.tsx`

The main upload page.

Responsibilities:

* let the user choose a CT scan file
* show selected file details
* trigger analysis request
* show loading state
* navigate to results page after success

---

### `pages/ResultsPage.tsx`

Shows the analysis output.

Responsibilities:

* show predicted class
* show confidence score
* show class probabilities
* show CT middle slice image
* show Grad-CAM visualization
* show file information
* allow user to analyze another scan or view history

---

### `pages/HistoryPage.tsx`

Shows earlier saved analyses.

Responsibilities:

* fetch saved history from backend
* list previous records
* allow user to inspect previous results
* allow delete action

---

### `pages/admin/AdminDashboard.tsx`

The admin home page, accessible at `/admin`.

Responsibilities:

* show a greeting with the logged-in admin's user ID
* show navigation cards linking to:
  * Access Requests
  * Users

Only visible in the navbar when the user has `role === "admin"`.

---

### `pages/admin/AccessRequestsPage.tsx`

The main admin tool for reviewing staff access requests.

Responsibilities:

* list all pending access requests with full structured detail:
  * First name
  * Last name
  * Personnummer
  * Email
  * Mobile
  * Position
  * Submitted date
* open an approval modal that shows:
  * auto-generated user ID (using `generateUserId`)
  * auto-generated temporary password (using `generateTempPassword`)
  * copy buttons for both fields
* confirm approval — calls backend to create the user account
* reject a request
* show handled (approved / rejected) requests in a separate section with status badges
* credentials are cached per request so reopening the modal shows the same values

---

### `pages/admin/UsersPage.tsx`

The admin user management page, accessible at `/admin/users`.

Responsibilities:

* list all registered users with their details
* edit a user's first name, last name, email, mobile, position, and role
* delete a user account (e.g. when an employee leaves)
* reset a user's password
* search/filter users

---

## 4.10 Styling

### `index.css`

The main global stylesheet.

Responsibilities:

* define theme variables for dark and light mode
* define fonts
* style navbar, logo, nav links, burger, dropdowns
* style auth pages (login/register/change-password cards and forms)
* style admin pages: page layout, section headers, count badges, request cards with detail grids, approve/reject buttons, modal overlay, modal card with copy rows
* style result pages and history cards
* style buttons, inputs, selects, error messages
* control responsive layout

---

## 5. Backend (.NET API) documentation

## 5.1 Purpose of the .NET backend

The ASP.NET Core backend acts as the middle layer between frontend and Python model service.

Responsibilities:

* authenticate users (userId + password → JWT)
* issue JWT tokens with role and userId claims
* receive and store access requests from staff
* allow admins to approve or reject requests and create accounts
* allow admins to manage users (CRUD)
* receive upload requests from frontend
* forward files to Python service
* receive inference results from Python
* save analysis records in database
* return data to frontend
* provide history endpoints

---

## 5.2 Main backend startup

### `Program.cs`

The main startup file of the .NET API.

Responsibilities:

* register controllers
* register Swagger
* configure SQLite database
* configure CORS
* configure JWT authentication
* register HttpClient for Python service
* apply database migrations automatically on startup
* **seed a default admin account** (`admin01`) if no admin user exists in the database

The seed admin is used during development and first deployment so the system always has at least one admin that can log in and manage users.

---

## 5.3 Configuration

### `appsettings.json`

Stores application configuration values.

Typical values:

* SQLite connection string
* Python service base URL
* JWT secret
* JWT issuer
* JWT audience
* token expiry settings

---

## 5.4 Controllers

### `Controllers/AuthController.cs`

Handles authentication endpoints.

Endpoints:

* `POST /api/auth/login`
* `POST /api/auth/change-password`

Responsibilities:

* validate user input
* find user by userId
* verify password hash with BCrypt
* generate JWT token containing userId, role, and email claims
* include `mustChangePassword` flag in login response
* on change-password: verify current password, hash and save new password, set `MustChangePassword = false`

---

### `Controllers/AccessRequestsController.cs`

Handles the staff onboarding request flow.

Endpoints:

* `POST /api/access-requests` — public, no auth required
* `GET /api/access-requests` — admin only
* `POST /api/access-requests/{id}/approve` — admin only
* `POST /api/access-requests/{id}/reject` — admin only

Responsibilities:

* receive access request submissions from the public form
* list all requests for admin review
* on approve: create a new `User` record with the provided userId and hashed temp password, mark request as approved, set `MustChangePassword = true`
* on reject: mark request as rejected

---

### `Controllers/AdminController.cs`

Handles user management for admins.

Endpoints:

* `GET /api/admin/users` — list all users
* `PUT /api/admin/users/{id}` — update user fields
* `DELETE /api/admin/users/{id}` — delete a user account
* `POST /api/admin/users/{id}/reset-password` — set a new password for a user

All endpoints require admin role.

---

### `Controllers/AnalyzeController.cs`

Handles the CT upload and inference endpoint.

Endpoint:

* `POST /api/analyze`

Responsibilities:

* require authentication
* receive uploaded file from frontend
* validate uploaded file
* forward file to Python service
* parse Python response
* save analysis result in database
* return response to frontend

---

### `Controllers/AnalysisHistoryController.cs`

Handles history-related endpoints.

Endpoints:

* `GET /api/history`
* `GET /api/history/{id}`
* `DELETE /api/history/{id}`

Responsibilities:

* find current authenticated user from JWT
* return only that user's saved analysis records
* return detail for one analysis
* delete records

---

## 5.5 Data layer

### `Data/AppDbContext.cs`

Defines the Entity Framework database context.

Responsibilities:

* expose `Users` DbSet
* expose `AnalysisResults` DbSet
* expose `AccessRequests` DbSet
* configure relations, indexes, and EF Core mappings

---

## 5.6 DTOs

### `Dtos/AuthDtos.cs`

Contains request and response shapes for auth.

* `LoginRequest` — userId + password
* `LoginResponse` — token + userId + role + mustChangePassword
* `ChangePasswordRequest` — currentPassword + newPassword

---

### `Dtos/AnalyzeDtos.cs`

Contains DTOs for analysis-related responses.

* Python service response DTO
* Frontend/backend analysis response DTO

---

### `Dtos/AnalyzeUploadRequest.cs`

Contains the upload request model wrapping `IFormFile`.

---

## 5.7 Models

### `Models/User.cs`

Represents a user in the database.

Fields:

* `Id` — internal database ID
* `UserId` — system-generated login identifier (e.g. `yobe2801`)
* `FirstName`
* `LastName`
* `Email`
* `MobileNumber`
* `Position` — job role (Doctor, Nurse, Radiologist, etc.)
* `Role` — system role (`user` or `admin`)
* `PasswordHash`
* `MustChangePassword` — set to `true` when account is created by admin; cleared after first password change
* `CreatedAt`

---

### `Models/AccessRequest.cs`

Represents a staff access request submitted through the public form.

Fields:

* `Id`
* `FirstName`
* `LastName`
* `Personnummer` — 11-digit Norwegian national ID
* `MobileNumber`
* `Email`
* `Position`
* `Status` — `pending`, `approved`, or `rejected`
* `SubmittedAt`

---

### `Models/AnalysisResult.cs`

Represents a saved analysis result linked to a user.

Fields:

* `Id`
* `UserId`
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

---

## 5.8 Migrations

The `Migrations` folder contains Entity Framework migration files.

The migration is regenerated cleanly with:

```bash
dotnet ef migrations add InitialCreate
dotnet ef database update
```

The app also runs `db.Database.Migrate()` automatically on startup, so the database is always up to date without manual steps.

---

## 5.9 Database

### `deeplungct.db`

The SQLite database file.

It stores:

* users
* access requests
* saved analysis results

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

---

## 6.2 Python startup API

### `app.py`

The FastAPI entry point.

Endpoints:

* `GET /health`
* `POST /analyze`

---

## 6.3 Inference logic

### `infer.py`

The main inference pipeline.

Responsibilities:

* read NIfTI bytes
* convert to tensor
* preprocess the CT volume
* run the PyTorch model
* compute probabilities
* choose prediction class
* generate Grad-CAM
* generate middle-slice image
* return all outputs as Python dictionary

---

## 6.4 Model definition

### `model.py`

Defines the neural network architecture.

Responsibilities:

* define the 3D ResNet-style model structure
* create convolution blocks and residual blocks
* expose the final model class used by inference

---

## 6.5 Model checkpoint

### `checkpoints/resnet3d_latest.pth`

Contains the trained model weights.
Without this file, inference cannot produce real predictions.

---

## 6.6 Python dependencies

### `requirements.txt`

Lists Python packages required for the service:

* `fastapi`
* `uvicorn`
* `torch`
* `torchio`
* `SimpleITK`
* `numpy`
* `Pillow`
* `python-multipart`

---

## 7. End-to-end request flows

## 7.1 Access request flow (new staff member)

1. Staff member opens `/register` (Access Request form).
2. Fills in: first name, last name, personnummer, mobile, private email, position.
3. Frontend validates personnummer (must be 11 digits).
4. Frontend sends `POST /api/access-requests`.
5. Backend saves the request with status `pending`.
6. Staff member sees a success message: "Your request has been sent. The admin will contact you."

---

## 7.2 Admin approval flow

1. Admin logs in and navigates to **Dashboard → Access Requests**.
2. Admin sees all pending requests with full detail:
   * First name, last name, personnummer, email, mobile, position, submitted date.
3. Admin clicks **Approve**.
4. A modal opens showing:
   * Auto-generated user ID (e.g. `yobe2801`) using name initials + birth day from personnummer.
   * Auto-generated 10-character temporary password.
   * Copy buttons for both.
5. Admin copies and sends credentials to the staff member (e.g. via email or phone).
6. Admin clicks **Confirm & create account**.
7. Backend creates the user account with `MustChangePassword = true`.
8. Request status changes to `approved`.

---

## 7.3 First login and password change flow

1. Staff member logs in at `/login` with their generated user ID and temporary password.
2. Backend returns `mustChangePassword: true` in the login response.
3. Frontend redirects to `/change-password`.
4. Staff member enters current password and sets a new password.
5. Backend verifies current password, saves the new hash, and sets `MustChangePassword = false`.
6. Frontend redirects to `/analyze`.

---

## 7.4 Login flow (returning user)

1. User opens `/login`.
2. Enters userId and password.
3. Backend finds the user and verifies the password hash.
4. Backend generates a JWT token with userId and role claims.
5. Frontend stores token, userId, and role in `localStorage`.
6. Navbar updates to show the userId and (if admin) the Dashboard link.
7. User is redirected to `/analyze`.

---

## 7.5 Analyze flow

1. User opens Analyze page.
2. User uploads `.nii` or `.nii.gz` file.
3. Frontend sends file to `POST /api/analyze`.
4. Backend verifies JWT.
5. Backend forwards file to Python `/analyze`.
6. Python service loads and preprocesses the file.
7. Python model predicts benign or malignancy.
8. Python generates class probabilities, middle slice image, and Grad-CAM image.
9. Python returns JSON to backend.
10. Backend saves result to SQLite.
11. Backend returns result to frontend.
12. Frontend opens Results page.

---

## 7.6 History flow

1. User opens History page.
2. Frontend requests `GET /api/history`.
3. Backend identifies user from JWT.
4. Backend returns only that user's records.
5. Frontend displays the saved records.

---

## 7.7 Admin user management flow

1. Admin navigates to **Dashboard → Users**.
2. Admin sees a list of all user accounts.
3. Admin can:
   * **Edit** — update name, email, mobile, position, or role.
   * **Reset password** — set a new temporary password and mark `MustChangePassword = true`.
   * **Delete** — permanently remove the account (used when an employee leaves).

---

## 8. Authentication design

Authentication is based on JWT.

### How it works

* After login, backend returns a JWT token.
* Frontend stores token, userId, and role in `localStorage`.
* Frontend sends token in the `Authorization: Bearer` header on protected requests.
* Backend validates token on protected endpoints.
* Role claim is used to protect admin-only endpoints.

### User ID format

User IDs are system-generated and not chosen by the user.

Format: `[2-char first name][2-char last name][2-digit birth day][2-digit counter]`

Example: Tor Eide born on 28th → `toei2801`

The counter (`01`) only increments if another user already has the same prefix.

### First-login password flag

When an account is created by the admin, `MustChangePassword` is set to `true`.
The JWT login response includes this flag.
The frontend redirects the user to `/change-password` before allowing access to the rest of the app.

---

## 9. Database design

The system uses 3 entities:

### User

Represents a system account. Created by admin after approving an access request. Contains profile fields, login credentials (hashed), role, and first-login flag.

### AccessRequest

Represents a pending or handled access request from a staff member. Stores the submitted personal information and the outcome (pending / approved / rejected).

### AnalysisResult

Represents one saved CT scan analysis linked to a user. Stores the prediction, confidence, visualization images, and file metadata.

### Relationships

* One `User` can have many `AnalysisResult` records.
* One `AccessRequest` leads to at most one `User` (after approval).

---

## 10. Error handling

Examples of errors handled in the project:

* invalid login credentials
* wrong current password during password change
* missing uploaded file
* unsupported file format
* Python service unavailable
* invalid model response
* unauthorized access to protected routes
* admin-only routes accessed by non-admin users
* access request not found
* user not found during admin operations
* duplicate user ID (handled by counter increment in generator)

---

## 11. Styling and UI design notes

The application uses a dark clinical UI style with support for theme switching.

Main design goals:

* modern but clean look
* readable data cards with structured label:value detail rows
* clear result visualization
* simple auth flow
* professional medical-system feel
* admin panel that feels structured and efficient

The admin pages use consistent section headers with count badges, expanded detail cards for requests, and a modal-based approval flow with copyable credentials.

---

## 12. Current strengths of the project

* clear separation between frontend, backend, and AI service
* admin-controlled user management — no uncontrolled self-registration
* auto-generated user IDs based on name and birth day
* first-login forced password change
* role-based access control (user vs admin) enforced on both frontend and backend
* full admin CRUD for user accounts
* structured access request review with full staff detail display
* modern React frontend with role-aware navbar
* dedicated .NET business/API layer
* separate Python model service for inference
* saved user-specific analysis history
* Grad-CAM visualization for explainability
* SQLite makes local development simple
* JWT auth with role claims

---

## 13. Current limitations

* SQLite is suitable for development, not large-scale production
* model prediction is for demonstration and not clinical use
* no email system — admin must manually forward credentials to staff
* no token refresh mechanism
* no audit log of admin actions
* no pagination yet on user/history lists

---

## 14. Future improvements

* automated email delivery of credentials on approval
* add refresh token support
* add audit logging for admin actions
* move from SQLite to PostgreSQL
* add pagination, search, and filtering on user and history lists
* improve Grad-CAM quality and explainability display
* add result details modal from history
* deploy backend and Python service in separate containers
* add automated tests for auth and admin flows

---

## 15. Technologies used

### Frontend

* React
* TypeScript
* React Router
* CSS (custom design system in `index.css`)

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

Bachelor-CRAI is a multi-layer application for medical image analysis with a full staff management system.

The frontend handles user interaction and admin tooling. The .NET backend handles authentication, user management, data storage, and API logic. The Python service handles AI inference and image visualization.

The project demonstrates how a modern web application can integrate:

* secure admin-controlled user onboarding
* role-based access control
* medical file upload
* AI-based classification
* explainable visualization
* persistent user history

It is a solid foundation for a bachelor project because it combines:

* frontend development
* backend development
* database management
* authentication and authorization
* AI model integration
* medical imaging workflow concepts
* admin panel design

---
