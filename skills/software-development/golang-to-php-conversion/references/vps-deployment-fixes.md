# VPS Deployment Fixes & Workarounds

Session: 2026-07-03T04:05:00Z - 2026-07-03T04:51:00Z  
Context: Full-stack PHP + MySQL + Vue.js deployment to Ubuntu VPS

## Composer Broken - Manual Dependency Installation

### Issue
System composer fails with `Class "Normalizer" not found` error when trying to install dependencies on fresh VPS.

**Error:**
```
Fatal error: Uncaught Error: Class "Normalizer" not found in 
/usr/share/php/Symfony/Component/Console/Helper/Helper.php:65
```

**Root Cause:** Missing PHP `intl` extension on VPS.

### Fix 1: Install PHP-INTL Extension

```bash
# Install missing extension
apt-get install -y php8.1-intl

# Verify installation
php -m | grep intl

# Now composer works
cd /var/www/project && composer install
```

### Fix 2: Install Dependencies Individually (If Composer Still Broken)

If composer system-wide is broken beyond repair, install critical dependencies directly:

```bash
cd /var/www/project

# Install firebase/php-jwt (most critical for JWT auth)
COMPOSER_ALLOW_SUPERUSER=1 composer require firebase/php-jwt

# Install other dependencies individually
COMPOSER_ALLOW_SUPERUSER=1 composer require vlucas/phpdotenv
COMPOSER_ALLOW_SUPERUSER=1 composer require guzzlehttp/guzzle
COMPOSER_ALLOW_SUPERUSER=1 composer require intervention/image
```

**Environment variable:** `COMPOSER_ALLOW_SUPERUSER=1` required when running composer as root.

## MySQL Timezone Error

### Issue
API fails with: `Unknown or incorrect time zone: 'Asia/Jakarta'`

**Root Cause:** MySQL timezone tables not loaded on VPS.

### Fix: Load MySQL Timezone Data

```bash
# Load timezone data into MySQL
mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root mysql

# Test timezone works
mysql -u dbuser -p'password' -e "SELECT CONVERT_TZ('2026-01-01 12:00:00', 'UTC', 'Asia/Jakarta');"
```

**Expected output:** Returns converted timestamp (not NULL).

**Common warnings to ignore:**
```
Warning: Unable to load '/usr/share/zoneinfo/iso3166.tab' as time zone. Skipping it.
Warning: Unable to load '/usr/share/zoneinfo/leap-seconds.list' as time zone. Skipping it.
```

These are metadata files, not timezone data — warnings are harmless.

## Nginx Config: SPA + API on Same Domain

### Issue
Nginx serves `index.php` (returns JSON error) instead of `index.html` (Vue.js SPA frontend) when accessing root URL.

**Symptom:**
```bash
curl http://185.245.61.91/
# Returns: {"success":false,"message":"Route not found","path":"","method":"GET"}
# Expected: HTML content of index.html
```

**Root Cause:** Nginx `index` directive prioritizes `index.php` over `index.html`.

### Fix: Prioritize index.html for Root, Keep PHP for /api/*

```nginx
server {
    listen 80;
    server_name 185.245.61.91;
    
    root /var/www/smart-lms/public;
    
    # CRITICAL: index.html BEFORE index.php
    index index.html index.php;
    
    access_log /var/log/nginx/smart-lms-access.log;
    error_log /var/log/nginx/smart-lms-error.log;
    
    # Serve static files first, fall back to index.html for SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # PHP-FPM for API endpoints
    location ~ \.php$ {
        fastcgi_pass unix:/run/php/php8.1-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
    
    # Block access to hidden files
    location ~ /\.ht {
        deny all;
    }
}
```

**Key changes:**
1. `index index.html index.php;` — HTML first, PHP second
2. `try_files $uri $uri/ /index.html;` — SPA routing support (all non-file URLs → index.html)
3. `location ~ \.php$` — PHP only for .php files (API routes via index.php)

**Apply changes:**
```bash
# Test config
nginx -t

# Reload if valid
systemctl reload nginx
```

**Result:**
- Root URL (`/`) → serves `index.html` (Vue.js SPA)
- API URLs (`/api/*`) → routed through `index.php` (PHP backend)
- Static assets (`/assets/*`) → served directly by Nginx

## JWT Library Missing - firebase/php-jwt

### Issue
Login API fails with: `Class "Firebase\JWT\JWT" not found in JWTHelper.php`

**Root Cause:** Composer dependencies not installed on VPS (vendor/ directory missing firebase/php-jwt).

### Fix: Install PHP-JWT via Composer

```bash
cd /var/www/project

# Install firebase/php-jwt
COMPOSER_ALLOW_SUPERUSER=1 composer require firebase/php-jwt --no-interaction

# Verify installation
ls vendor/firebase/php-jwt/src/JWT.php
```

**Alternative (if composer.json already lists firebase/php-jwt):**
```bash
cd /var/www/project
COMPOSER_ALLOW_SUPERUSER=1 composer install --no-dev --optimize-autoloader
```

**Test JWT now works:**
```bash
curl -X POST http://185.245.61.91/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123"}'
```

**Expected:** Returns JWT token in JSON response.

## Password Hashing for Test Users

### Issue
Need to create test users with bcrypt password hashes compatible with PHP's `password_verify()`.

### Solution: Generate Hash on VPS

```bash
# On VPS with PHP installed
ssh user@vps-host

# Generate bcrypt hash
php -r "echo password_hash('admin123', PASSWORD_DEFAULT);"
# Output: $2y$10$L8piARXSD1dGrhu1wbja4Om3AGybyLZw9RZDrkFPEG0xy.bMIF4OG
```

**Insert user with generated hash:**
```sql
INSERT INTO users (name, email, password, role, active) 
VALUES (
    'Admin Test',
    'admin@test.com',
    '$2y$10$L8piARXSD1dGrhu1wbja4Om3AGybyLZw9RZDrkFPEG0xy.bMIF4OG',
    'admin',
    1
);
```

**Test login:**
```bash
curl -X POST http://server/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123"}'
```

**Important:** Use the VPS's PHP to generate hashes — ensures compatibility with VPS's PHP version and bcrypt implementation.

## Git Ownership Issues on VPS

### Issue
`git pull` fails with: `fatal: detected dubious ownership in repository`

**Root Cause:** Repository owned by one user (www-data), git command run as another (root).

### Fix: Add Repository to Git Safe Directories

```bash
# Add to git's safe directory list
git config --global --add safe.directory /var/www/project

# Now git pull works
cd /var/www/project && git pull origin main
```

**Alternative (reset ownership):**
```bash
chown -R www-data:www-data /var/www/project
```

## VPS Prerequisites - Full LEMP Stack Setup

### Quick Install Script (Ubuntu 22.04)

```bash
# Update repositories
apt-get update

# Add PHP repository (for PHP 8.1)
apt-get install -y software-properties-common
add-apt-repository -y ppa:ondrej/php
apt-get update

# Install PHP 8.1 + extensions
apt-get install -y \
    php8.1-cli \
    php8.1-fpm \
    php8.1-mysql \
    php8.1-mbstring \
    php8.1-xml \
    php8.1-curl \
    php8.1-zip \
    php8.1-intl

# Install Nginx
apt-get install -y nginx

# Install MySQL 8.0
apt-get install -y mysql-server

# Install Composer
apt-get install -y composer

# Install Git
apt-get install -y git

# Install unzip (for Composer)
apt-get install -y unzip

# Install sshpass (for automated SSH operations)
apt-get install -y sshpass

# Start services
systemctl start mysql
systemctl enable mysql
systemctl start php8.1-fpm
systemctl enable php8.1-fpm
systemctl start nginx
systemctl enable nginx

# Verify installations
php -v              # PHP 8.1.x
mysql --version     # MySQL 8.0.x
nginx -v            # Nginx 1.18.x
composer --version  # Composer 2.x
```

## Frontend Build Output Location (Vite)

### Issue
Vite builds to `../public/` instead of `dist/` when output is configured in `vite.config.js`.

**Expected:** Build output in `frontend/dist/`  
**Actual:** Build output in `public/` (parent directory)

**vite.config.js:**
```javascript
export default defineConfig({
  build: {
    outDir: '../public',  // Relative to frontend/
    emptyOutDir: false
  }
})
```

**Result:** Files created in `/project/public/` (parallel to `/project/frontend/`).

**Deployment strategy:**
1. Build locally: `cd frontend && npm run build`
2. Output goes to `public/` directory (not `frontend/dist/`)
3. Copy via scp: `scp -r public/* user@vps:/var/www/project/public/`

**Directory structure after build:**
```
project/
├── frontend/
│   ├── src/
│   ├── vite.config.js
│   └── package.json
├── public/
│   ├── index.html        # Vite build output
│   ├── index.php         # PHP backend entry point
│   ├── assets/
│   │   ├── index-*.js
│   │   └── index-*.css
│   ├── sw.js             # Service worker
│   └── manifest.webmanifest
```

**Nginx serves from:** `/var/www/project/public/`

## Deployment Checklist - VPS Production

Pre-deployment verification (do BEFORE starting deployment):

**Infrastructure:**
- [ ] VPS accessible via SSH (test: `ssh user@host`)
- [ ] PHP 8.1+ installed (`php -v`)
- [ ] PHP extensions: cli, fpm, mysql, mbstring, xml, curl, zip, intl
- [ ] Nginx installed and running (`nginx -v`, `systemctl status nginx`)
- [ ] MySQL 8.0+ installed (`mysql --version`)
- [ ] Composer installed (`composer --version`)
- [ ] Git installed (`git --version`)

**Database:**
- [ ] MySQL timezone tables loaded (`mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root mysql`)
- [ ] Database created (`CREATE DATABASE dbname;`)
- [ ] Database user created with permissions (`GRANT ALL ON dbname.* TO 'user'@'localhost';`)
- [ ] Schema imported (`mysql -u user -p dbname < schema.sql`)
- [ ] Test timezone: `SELECT CONVERT_TZ(NOW(), 'UTC', 'Asia/Jakarta');` returns non-NULL

**Application:**
- [ ] Code cloned to VPS (`/var/www/project`)
- [ ] `.env` configured with correct DB credentials
- [ ] Composer dependencies installed (`composer install` or manual `composer require`)
- [ ] Permissions set (`chown -R www-data:www-data /var/www/project`)
- [ ] Nginx config created and enabled (`/etc/nginx/sites-available/project`)
- [ ] Nginx config tested (`nginx -t`) and reloaded (`systemctl reload nginx`)
- [ ] Frontend built and deployed (`npm run build` → copy to `public/`)
- [ ] Test user created with bcrypt password hash

**Verification:**
- [ ] Root URL serves HTML: `curl http://server/` returns `<!DOCTYPE html>`
- [ ] API responds: `curl http://server/api/students` returns JSON
- [ ] Login works: `curl -X POST http://server/api/auth/login -d {...}` returns JWT token
- [ ] Frontend loads in browser: Navigate to `http://server/` shows Vue.js app

## Common Pitfalls

### 1. Composer Normalizer Error
**Fix:** `apt-get install -y php8.1-intl`

### 2. MySQL Timezone Error
**Fix:** `mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root mysql`

### 3. Nginx Serves PHP Instead of HTML
**Fix:** Change `index` directive to `index index.html index.php;`

### 4. JWT Class Not Found
**Fix:** `COMPOSER_ALLOW_SUPERUSER=1 composer require firebase/php-jwt`

### 5. Git Dubious Ownership
**Fix:** `git config --global --add safe.directory /path/to/repo`

### 6. Permission Denied Errors
**Fix:** `chown -R www-data:www-data /var/www/project`

### 7. PHP-FPM Not Running
**Fix:** `systemctl start php8.1-fpm && systemctl enable php8.1-fpm`

### 8. Database Connection Fails
**Check:** `.env` credentials match MySQL user (`DB_USER`, `DB_PASS`, `DB_DATABASE`)

### 9. CORS Errors in Browser
**Fix:** Add CORS headers to PHP or Nginx (see main skill CORS section)

### 10. Frontend Assets 404
**Check:** Nginx root points to correct directory (`/var/www/project/public`)
