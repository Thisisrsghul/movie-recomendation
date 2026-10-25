# Employee Management System

A web-based Employee Management System built with **Java**, **Spring Boot**, **Spring Data JPA**, and **SQLite**. It provides a browser-based interface for managing employee records, attendance, payroll, and user accounts.

> This is a learning/demo project. Review and improve the security controls before using it with real employee data.

## Features

- User sign-up and login
- Employee record management: create, view, update, and delete
- Attendance recording and attendance history
- Payroll records with bonuses and deductions
- Total employee salary expense endpoint
- SQLite database for local persistence
- Browser-based frontend built with HTML, CSS, and JavaScript

## Tech Stack

- **Language:** Java
- **Framework:** Spring Boot 3.5.3
- **Java target:** Java 17 (the project was also observed starting successfully with Java 25)
- **Backend:** Spring Web, Spring Data JPA, Hibernate
- **Database:** SQLite
- **Build tool:** Maven Wrapper
- **Frontend:** HTML, CSS, JavaScript

## Prerequisites

- JDK 17 or later
- A web browser
- Internet access for the first build, so Maven can download dependencies

The repository includes `mvnw` and `mvnw.cmd`, so installing Maven separately is not required.

Verify Java in PowerShell:

```powershell
java -version
```

## Download the Project

### Option 1: Clone with Git

```powershell
git clone https://github.com/Thisisrsghul/employee-management.git
cd employee-management
```

### Option 2: Download ZIP

1. Open the repository: https://github.com/Thisisrsghul/employee-management
2. Select **Code → Download ZIP**.
3. Extract the ZIP.
4. Open a terminal in the extracted `employee-management-main` folder—the folder that contains `pom.xml` and `mvnw.cmd`.

**Important:** If the extracted folder is nested inside another folder, change into the inner project folder before running the commands. Running the wrapper from a parent folder will result in a “command not found” error.

Check that you are in the project root:

```powershell
Test-Path .\pom.xml
Test-Path .\mvnw.cmd
```

Both commands should return `True`.

## Run on Windows

Open PowerShell in the folder containing `pom.xml`, then run:

```powershell
.\mvnw.cmd spring-boot:run
```

Wait for a message similar to:

```text
Tomcat started on port 8080 (http)
Started EmployeeManagementApplication
```

Keep this terminal open while using the application.

Open the app in your browser:

**http://localhost:8080/**

To stop the application, press `Ctrl + C` in the terminal.

### Run on Linux or macOS

From the project root:

```bash
chmod +x ./mvnw
./mvnw spring-boot:run
```

Then visit http://localhost:8080/.

## Demo Login

The login page displays these demo credentials:

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Manager | `manager` | `manager123` |
| Employee | `emp1` | `emp123` |

These accounts are present in the sample database included with the project. If you replace or remove that database, the credentials may no longer work. You can also use **Create an account** on the login page.

**Security warning:** The current authentication code compares passwords directly, and the sample database stores passwords in plaintext. These demo credentials must not be reused for personal or production accounts. Before deployment, implement password hashing, authorization checks, input validation, and appropriate protection for sensitive employee/payroll data.

## Build and Test

Run tests:

```powershell
.\mvnw.cmd test
```

Build the JAR:

```powershell
.\mvnw.cmd clean package
```

Run the packaged application after a successful build:

```powershell
java -jar target\employee-management-0.0.1-SNAPSHOT.jar
```

For Linux/macOS, use `./mvnw` and `target/employee-management-0.0.1-SNAPSHOT.jar`.

## Database Configuration

The database configuration is in `src/main/resources/application.properties`.

- Database engine: SQLite
- JDBC URL: `jdbc:sqlite:employee_management.db`
- Database file: `employee_management.db` in the application working directory
- Hibernate schema setting: `spring.jpa.hibernate.ddl-auto=update`
- Server port: `8080`

Run the app from the project root so the relative SQLite database path resolves as expected. Back up the database before replacing or deleting it. The repository's sample database contains example records and should be treated as demo data.

## REST API Reference

Base URL: `http://localhost:8080`

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/auth/signup` | Register a user (JSON body) |
| `POST` | `/api/auth/login` | Authenticate a user (JSON body) |
| `GET` | `/api/employees` | Get all employees |
| `GET` | `/api/employees/{id}` | Get one employee |
| `POST` | `/api/employees` | Create an employee (JSON body) |
| `PUT` | `/api/employees/{id}` | Update an employee (JSON body) |
| `DELETE` | `/api/employees/{id}` | Delete an employee |
| `GET` | `/api/employees/salary/total` | Get total salary expense |
| `GET` | `/api/attendance` | Get all attendance records |
| `GET` | `/api/attendance/employee/{employeeId}` | Get attendance for one employee |
| `POST` | `/api/attendance?employeeId={id}&date=YYYY-MM-DD&status={status}` | Record attendance |
| `GET` | `/api/payroll` | Get all payroll records |
| `GET` | `/api/payroll/employee/{employeeId}` | Get payroll for one employee |
| `POST` | `/api/payroll?employeeId={id}&bonus={amount}&deductions={amount}&month=YYYY-MM-DD` | Create a payroll record |

For the signup and login endpoints, send JSON request bodies. Employee create/update endpoints also accept JSON. Attendance and payroll creation use URL query parameters; use URL encoding when necessary.

## Project Structure

```text
employee-management-main/
├── .mvn/
│   └── wrapper/
├── mvnw
├── mvnw.cmd
├── pom.xml
├── employee_management.db
└── src/
    ├── main/
    │   ├── java/com/employee/
    │   │   ├── EmployeeManagementApplication.java
    │   │   ├── controller/
    │   │   ├── entity/
    │   │   ├── repository/
    │   │   └── service/
    │   └── resources/
    │       ├── application.properties
    │       └── static/
    │           ├── index.html
    │           ├── dashboard.html
    │           ├── auth.css
    │           ├── auth.js
    │           ├── script.js
    │           ├── dashboard.js
    │           └── style.css
    └── test/
```

## Troubleshooting

### `.\mvnw.cmd` is not recognized

Change directory to the folder containing `pom.xml` and `mvnw.cmd`:

```powershell
cd path\to\employee-management-main
dir pom.xml, mvnw.cmd
.\mvnw.cmd spring-boot:run
```

### Port 8080 is already in use

Stop the other process using port 8080, or change `server.port` in `src/main/resources/application.properties`.

### The browser cannot connect

Make sure the Spring Boot process is still running and that the terminal shows Tomcat started on port 8080. Use `http://localhost:8080/`, not HTTPS.

### Demo login does not work

Check that you are using the included `employee_management.db` and the demo credentials listed above. If you have replaced the database, create a new account using the signup page.

### Dependency download or build failure

Check your internet connection and rerun:

```powershell
.\mvnw.cmd spring-boot:run
```

## License

No license is specified in this repository. Add a `LICENSE` file if you want to define how others may use, modify, or distribute the project.
