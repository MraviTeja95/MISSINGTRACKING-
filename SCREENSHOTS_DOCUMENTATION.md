# 📸 UI/UX Screenshots Documentation

## Overview
This document provides detailed descriptions and visual layouts of all major screens in the TraceNet application. These screenshots guide users through the application's functionality.

---

## 1. Home Page / Landing Page (`/`)

### Description
Entry point for the application. Dark-themed modern UI with animated background.

### Screen Layout
```
┌────────────────────────────────────────────────────────────┐
│  TraceNet Logo        [Login] [Police Login] [Sign Up]     │
├────────────────────────────────────────────────────────────┤
│                                                             │
│              🔍 TRACENET - Missing Person Tracking          │
│                   & Crime Pattern Analysis                 │
│                                                             │
│              [Report Missing Person]  [View Cases]         │
│                                                             │
│                   ╔═══════════════════════╗               │
│                   ║  45 Missing Persons   ║               │
│                   ║  12 Found This Month  ║               │
│                   ║  156 Crime Incidents  ║               │
│                   ║  8 High-Risk Areas    ║               │
│                   ╚═══════════════════════╝               │
│                                                             │
├────────────────────────────────────────────────────────────┤
│ Features: • AI Face Recognition  • ML Crime Analytics      │
│           • Real-time Alerts     • Role-Based Access      │
└────────────────────────────────────────────────────────────┘
```

### Interactive Elements
- **Login Button**: Redirects to `/login`
- **Police Login**: Redirects to `/police-login`
- **Sign Up**: Redirects to `/signup`
- **Report Button**: Quick link to `/report`
- **View Cases**: Link to `/missing-list`

### Color Scheme
- **Background**: Dark (#1a1a1a) with animated gradients
- **Text**: White (#ffffff)
- **Buttons**: Blue gradient (#0084ff)
- **Cards**: Semi-transparent dark (#2a2a2a)

---

## 2. Login Page (`/login`)

### Description
User authentication screen with role-based login options.

### Screen Layout
```
┌────────────────────────────────────────┐
│         TRACENET LOGIN                 │
├────────────────────────────────────────┤
│                                        │
│  ┌──────────────────────────────────┐ │
│  │  Login Type:                     │ │
│  │  ◉ Public    ○ Police  ○ Admin   │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ Username/Email                   │ │
│  │ [_____________________________]   │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ Password                         │ │
│  │ [____________________________•] 👁 │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ☐ Remember me                         │
│                                        │
│       [      LOGIN      ]              │
│                                        │
│  Don't have account? [Sign Up Here]    │
│  Forgot Password? [Reset Password]     │
│                                        │
└────────────────────────────────────────┘
```

### Features
- **Role Selection**: Public, Police, Admin
- **Credential Input**: Username/Email and Password
- **Remember Me**: Session persistence
- **Password Recovery**: Link to reset form
- **Sign Up Link**: Navigation to registration

### Validation
- ✓ Username/Email required
- ✓ Password min 8 characters
- ✓ Role-based access control
- ✓ Error messages on failed login

---

## 3. Sign Up Page (`/signup`)

### Description
User registration form for new accounts.

### Screen Layout
```
┌────────────────────────────────────────┐
│        CREATE NEW ACCOUNT              │
├────────────────────────────────────────┤
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ Full Name                        │ │
│  │ [_____________________________]   │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ Email Address                    │ │
│  │ [_____________________________]   │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ Username                         │ │
│  │ [_____________________________]   │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ Password                         │ │
│  │ [_____________________________]   │ │
│  │ Password strength: ███░░░░░░░░░░  │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ Account Type:                    │ │
│  │ ◉ Public    ○ Police Reporter    │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ☐ I agree to Terms & Conditions      │
│                                        │
│      [    SIGN UP    ]  [Cancel]      │
│                                        │
│  Already have account? [Login Here]    │
│                                        │
└────────────────────────────────────────┘
```

### Features
- Full name, email, username, password input
- Account type selection
- Password strength indicator
- Terms & Conditions checkbox
- Already registered link to login

---

## 4. Report Missing Person (`/report`)

### Description
Form for the public to report missing persons with photo upload.

### Screen Layout
```
┌───────────────────────────────────────────────────────┐
│     REPORT MISSING PERSON                             │
├───────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │ Personal Details                                │ │
│  ├─────────────────────────────────────────────────┤ │
│  │                                                 │ │
│  │  Full Name *                                    │ │
│  │  [_________________________________]            │ │
│  │                                                 │ │
│  │  Age                  Last Known Location *     │ │
│  │  [_______]            [__________________]      │ │
│  │                                                 │ │
│  │  Physical Description                           │ │
│  │  Height:  [_____]  Build:  [_______]            │ │
│  │  Hair Color: [________]  Eye Color: [_______]   │ │
│  │                                                 │ │
│  │  Distinguishing Features (scars, tattoos, etc.) │ │
│  │  [                                            ] │ │
│  │  [                                            ] │ │
│  │  [                                            ] │ │
│  └─────────────────────────────────────────────────┘ │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │ Photo Upload (REQUIRED) *                       │ │
│  ├─────────────────────────────────────────────────┤ │
│  │                                                 │ │
│  │       📷 Drag & Drop Photo Here                 │ │
│  │       or [Browse Files]                         │ │
│  │                                                 │ │
│  │       Accepted: JPG, JPEG, PNG (Max 16MB)      │ │
│  │                                                 │ │
│  └─────────────────────────────────────────────────┘ │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │ Reporter Information                            │ │
│  ├─────────────────────────────────────────────────┤ │
│  │                                                 │ │
│  │  Your Contact Number *                          │ │
│  │  [_________________________________]            │ │
│  │                                                 │ │
│  │  Email Address *                                │ │
│  │  [_________________________________]            │ │
│  │                                                 │ │
│  │  Relationship to Missing Person                 │ │
│  │  [_________________________________]            │ │
│  │                                                 │ │
│  └─────────────────────────────────────────────────┘ │
│                                                       │
│       [    SUBMIT REPORT    ]  [Cancel]              │
│                                                       │
│  *  Required Fields                                  │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### Key Features
- Personal details form
- Photo drag-and-drop upload
- Reporter contact information
- Form validation with error messages
- Success notification with case reference number

---

## 5. Missing Persons List (`/missing-list`)

### Description
Gallery/table view of all missing person reports with search and filter options.

### Screen Layout
```
┌─────────────────────────────────────────────────────────┐
│  MISSING PERSONS REGISTRY                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Search: [__________________________]  🔍             │
│  Filter: [Status ▼] [Age Range ▼] [Location ▼]       │
│          Sort: [Latest Reports ▼]                     │
│                                                         │
│  ┌──────────────────────┬──────────────────────────┐   │
│  │ ┌──────────────────┐ │  John Doe                │   │
│  │ │                  │ │  Age: 28 | Missing      │   │
│  │ │    📷 Photo      │ │  Last Seen: MG Road     │   │
│  │ │                  │ │  Reported: 3 days ago   │   │
│  │ └──────────────────┘ │  [View Details]         │   │
│  └──────────────────────┴──────────────────────────┘   │
│                                                         │
│  ┌──────────────────────┬──────────────────────────┐   │
│  │ ┌──────────────────┐ │  Sarah Johnson          │   │
│  │ │                  │ │  Age: 15 | Found        │   │
│  │ │    📷 Photo      │ │  Last Seen: Whitefield  │   │
│  │ │                  │ │  Reported: 2 weeks ago  │   │
│  │ └──────────────────┘ │  [View Details]         │   │
│  └──────────────────────┴──────────────────────────┘   │
│                                                         │
│  ┌──────────────────────┬──────────────────────────┐   │
│  │ ┌──────────────────┐ │  Michael Chen           │   │
│  │ │                  │ │  Age: 42 | Missing      │   │
│  │ │    📷 Photo      │ │  Last Seen: Koramangala │   │
│  │ │                  │ │  Reported: 1 week ago   │   │
│  │ └──────────────────┘ │  [View Details]         │   │
│  └──────────────────────┴──────────────────────────┘   │
│                                                         │
│  Showing 1-10 of 45  [← Previous] [1] [2] [3] [Next →] │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Features
- **Search Bar**: Full-text search by name
- **Filters**: Status, age range, location
- **Sorting**: By date reported, name, status
- **Grid View**: Photo + key details
- **Pagination**: Browse through reports
- **Detail View**: Click to see full person profile

---

## 6. Missing Person Details View

### Description
Detailed profile of a specific missing person with action buttons.

### Screen Layout
```
┌─────────────────────────────────────────────────────────┐
│  PERSON DETAILS - Case #MP-2026-045                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐                                       │
│  │              │   Name: John Doe                      │
│  │   📷 Photo   │   Age: 28 years old                   │
│  │              │   Gender: Male                        │
│  │              │   Status: 🔴 MISSING                  │
│  └──────────────┘   Reported: June 2, 2026             │
│                     Reporter: Jane Doe (Mother)        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Physical Description                            │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ Height: 5'9" | Build: Athletic                  │   │
│  │ Hair: Black | Eyes: Brown                       │   │
│  │ Tattoos: Dragon on left shoulder                │   │
│  │ Scars: Scar above right eyebrow                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Last Seen Information                           │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ Location: MG Road, Bangalore                    │   │
│  │ Date/Time: June 1, 2026 at 10:30 PM            │   │
│  │ Clothing: Blue jeans, white shirt               │   │
│  │ With: Friend (name unknown)                     │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Contact Information                             │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ Reporter: Jane Doe                              │   │
│  │ Phone: +91 98765 43210                          │   │
│  │ Email: jane.doe@email.com                       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [Report Update]  [Share Case]  [Mark as Found]        │
│  [AI Face Search] [Add to Watchlist]                   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Similar Profiles (AI Matched)                   │   │
│  │ [Person A] (75% match)                          │   │
│  │ [Person B] (68% match)                          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 7. Police Dashboard (`/dashboard`)

### Description
Comprehensive analytics dashboard for police officers and admin.

### Screen Layout
```
┌─────────────────────────────────────────────────────────────────┐
│  POLICE DASHBOARD - Welcome, Officer Smith                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ╔══════════════╗ ╔══════════════╗ ╔══════════════╗             │
│  ║ Missing:     ║ ║ Found:       ║ ║ Total Crimes:║             │
│  ║    45        ║ ║    12        ║ ║     156      ║             │
│  ║  Cases       ║ ║  Cases       ║ ║             ║             │
│  ╚══════════════╝ ╚══════════════╝ ╚══════════════╝             │
│                                                                 │
│  ┌──────────────────────┬──────────────────────────────────┐   │
│  │ High-Risk Areas      │ Crime Distribution (Last 30d)   │   │
│  ├──────────────────────┼──────────────────────────────────┤   │
│  │ 1. MG Road (8)       │                                  │   │
│  │ 2. Koramangala (6)   │  [Pie Chart]                     │   │
│  │ 3. Whitefield (5)    │  - Theft 35%                     │   │
│  │ 4. Jayanagar (4)     │  - Robbery 28%                   │   │
│  │ 5. Indiranagar (3)   │  - Assault 22%                   │   │
│  │                      │  - Other 15%                     │   │
│  └──────────────────────┴──────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 12-Month Crime Trends                                    │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ [Line Chart: Crime Count vs Missing Persons]             │   │
│  │ Jun '25: 12 crimes, 2 missing                           │   │
│  │ Jul '25: 14 crimes, 3 missing                           │   │
│  │ ... [trending upward]                                   │   │
│  │ Jun '26: 18 crimes, 4 missing                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Recent Activity                                          │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ • New missing person report: Sarah Johnson (age 15)      │   │
│  │ • Crime added: Robbery at Koramangala (Severity: 4)      │   │
│  │ • Face match found: 89% confidence - John Doe            │   │
│  │ • High-risk alert: MG Road (predicted High risk)         │   │
│  │ • Device registered: 2 new Android devices              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [Add Crime]  [Face Search]  [View Analytics]  [Export Report] │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Features
- **KPI Cards**: Missing, found, crime statistics
- **High-Risk Areas List**: Top locations by crime count
- **Crime Distribution**: Pie chart by crime type
- **12-Month Trends**: Line chart showing patterns
- **Recent Activity Feed**: Real-time updates
- **Action Buttons**: Quick access to main functions

---

## 8. Face Search Tool (`/face-search`)

### Description
AI-powered facial recognition interface for searching missing persons.

### Screen Layout
```
┌─────────────────────────────────────────────────────────┐
│  AI FACE RECOGNITION SEARCH                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Upload Query Image                                │ │
│  ├───────────────────────────────────────────────────┤ │
│  │                                                   │ │
│  │         📷 Drag & Drop Image Here                │ │
│  │         or [Browse Files]                         │ │
│  │                                                   │ │
│  │         Best results: Clear face photo           │ │
│  │         Accepted formats: JPG, PNG              │ │
│  │                                                   │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  Confidence Threshold: [████░░░░░░░░░░░░░░]  70%      │
│                                                         │
│              [    START SEARCH    ]                    │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Matching Results (Top 10)                         │ │
│  ├───────────────────────────────────────────────────┤ │
│  │                                                   │ │
│  │  1. John Doe          - Confidence: 89.3%  ✓    │ │
│  │     Age 28, Missing                              │ │
│  │     Last Seen: MG Road, 3 days ago              │ │
│  │     [View Profile] [Confirm Match] [Report]      │ │
│  │                                                   │ │
│  │  2. Michael Chen      - Confidence: 74.8%       │ │
│  │     Age 42, Missing                              │ │
│  │     Last Seen: Whitefield, 7 days ago           │ │
│  │     [View Profile] [Confirm Match]               │ │
│  │                                                   │ │
│  │  3. David Kumar       - Confidence: 68.2%       │ │
│  │     Age 35, Found                                │ │
│  │     Last Seen: Koramangala, 2 weeks ago         │ │
│  │     [View Profile]                               │ │
│  │                                                   │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ⓘ Confidence scores above 70% are recommended        │
│  ⓘ Results show top matches from 45 missing persons   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Key Features
- Drag-and-drop image upload
- Confidence threshold adjustment
- Ranked match results with percentages
- Person details in results
- Actions: View profile, confirm match, report

---

## 9. Crime Analytics Page

### Description
Detailed crime data visualization and analysis tools.

### Screen Layout
```
┌─────────────────────────────────────────────────────────────┐
│  CRIME ANALYTICS & HOTSPOT ANALYSIS                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Crime Heatmap (Geographic Distribution)             │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                                                     │   │
│  │  [Interactive Map with Crime Hotspots]             │   │
│  │                                                     │   │
│  │  🔴🔴 MG Road (High Risk)                          │   │
│  │    🟠 Koramangala (Medium Risk)                    │   │
│  │      🟡 Whitefield (Low Risk)                      │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────┬──────────────────────────────────┐   │
│  │ Location Stats   │ Crime Type Distribution         │   │
│  ├──────────────────┼──────────────────────────────────┤   │
│  │ Location  Count  │                                  │   │
│  │ MG Road    8     │  [Bar Chart]                     │   │
│  │ Koram.     6     │  Theft:     ████████ (45)       │   │
│  │ Whitef.    5     │  Robbery:   ██████ (32)         │   │
│  │ Jayanan.   4     │  Assault:   ████ (22)           │   │
│  │ Indiran.   3     │  Cybercrim: ██ (12)             │   │
│  │ Others     2     │  Other:     █ (5)               │   │
│  └──────────────────┴──────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Recent Crimes (Last 7 Days)                          │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ Date    | Location  | Type    | Severity | Details  │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ Jun 2   | MG Road   | Theft   |    3     | [...] │   │
│  │ Jun 2   | Koram.    | Robbery |    4     | [...] │   │
│  │ Jun 1   | Whitef.   | Assault |    4     | [...] │   │
│  │ Jun 1   | Jayana.   | Theft   |    2     | [...] │   │
│  │ May 31  | MG Road   | Robbery |    3     | [...] │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  [Add Crime]  [Export Data]  [Generate Report]             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. Notification Settings Page (`/notifications/settings`)

### Description
User settings for managing push notifications.

### Screen Layout
```
┌─────────────────────────────────────────────────────┐
│  NOTIFICATION SETTINGS                              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │ Notification Preferences                      │ │
│  ├───────────────────────────────────────────────┤ │
│  │                                               │ │
│  │  ☑ Enable Push Notifications                 │ │
│  │  ☑ Face Match Alerts                         │ │
│  │  ☑ High-Risk Area Warnings                   │ │
│  │  ☑ Case Status Updates                       │ │
│  │  ☑ New Missing Person Reports                │ │
│  │  ☐ Crime Analytics Digest                    │ │
│  │  ☑ Weekly Summary Report                     │ │
│  │                                               │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │ Registered Devices                            │ │
│  ├───────────────────────────────────────────────┤ │
│  │                                               │ │
│  │  🌐 Web Browser                               │ │
│  │     Platform: Web | Status: Active            │ │
│  │     Registered: June 1, 2026                  │ │
│  │     Last Used: 2 hours ago                    │ │
│  │     [Unregister Device]                       │ │
│  │                                               │ │
│  │  📱 Samsung Galaxy S21                        │ │
│  │     Platform: Android | Status: Active        │ │
│  │     Registered: May 15, 2026                  │ │
│  │     Last Used: 30 minutes ago                 │ │
│  │     [Unregister Device]                       │ │
│  │                                               │ │
│  │  📱 iPhone 13 Pro                             │ │
│  │     Platform: iOS | Status: Inactive          │ │
│  │     Registered: April 20, 2026                │ │
│  │     Last Used: 8 days ago                     │ │
│  │     [Unregister Device]                       │ │
│  │                                               │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │ Notification History (Last 30 Days)           │ │
│  ├───────────────────────────────────────────────┤ │
│  │                                               │ │
│  │  📩 Face Match Alert                          │ │
│  │     "Match found: 89% confidence - John Doe"  │ │
│  │     Sent: June 2, 2026 10:30 AM               │ │
│  │                                               │ │
│  │  🚨 High-Risk Alert                           │ │
│  │     "High-risk activity in MG Road area"      │ │
│  │     Sent: June 1, 2026 08:15 PM               │ │
│  │                                               │ │
│  │  📢 New Report                                │ │
│  │     "Sarah Johnson (age 15) reported missing" │ │
│  │     Sent: June 1, 2026 02:45 PM               │ │
│  │                                               │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│       [   SAVE SETTINGS   ]  [Cancel]              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 11. Unauthorized / 403 Page (`/unauthorized`)

### Description
Error page for insufficient access permissions.

### Screen Layout
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│           ❌ ACCESS DENIED                          │
│                                                     │
│   You do not have permission to access this page.  │
│                                                     │
│   Required Access Level: Police / Admin             │
│   Your Access Level: Public                         │
│                                                     │
│   To request access, contact your administrator.   │
│                                                     │
│          [Go to Home]  [Contact Admin]             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 12. Responsive Design Breakpoints

### Mobile (< 768px)
- Single-column layout
- Stack-based cards
- Touch-friendly buttons (48x48px min)
- Swipe navigation for galleries
- Collapsible navigation menu

### Tablet (768px - 1024px)
- Two-column layout for analytics
- Side navigation drawer
- Touch and mouse input support

### Desktop (> 1024px)
- Multi-column layouts
- Side navigation bar
- Hover effects
- Full feature display

---

## Design System Colors

| Element | Color Code | Usage |
|---------|-----------|-------|
| Dark Background | #1a1a1a | Main background |
| Card Background | #2a2a2a | Card/Modal backgrounds |
| Text Primary | #ffffff | Main text |
| Text Secondary | #b0b0b0 | Secondary text |
| Primary Button | #0084ff | Call-to-action |
| Success | #28a745 | Positive actions |
| Warning | #ffc107 | Warnings/Alerts |
| Danger | #dc3545 | Errors/Dangerous |
| Info | #17a2b8 | Information |

---

## Accessibility Features

✅ **WCAG 2.1 AA Compliant**
- High contrast ratios (4.5:1 for text)
- Keyboard navigation support
- Screen reader compatibility
- Alt text for all images
- ARIA labels for complex elements
- Focus indicators on all interactive elements

