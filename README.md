---

# Odoo Import Employee and Invoice API Guide

## Before You Start

1. **Create New Odoo Database or Use `setup/alterra.zip`**
   
2. **Install `alterra_bills` Module**

3. **Setup for Longpolling:**
   Follow the instructions at [Longpolling Setup Guide](https://odoo-development.readthedocs.io/en/latest/admin/longpolling.html).

4. **Setup for `queue_job`:**
   Refer to the configuration details in the [queue_job module documentation](https://apps.odoo.com/apps/modules/14.0/queue_job#configuration).

5. **Update `.conf` File:**
   Ensure your Odoo configuration file includes the following settings:
   ```
   workers = 6
   server_wide_modules = base,web,queue_job
   proxy_mode = True
   ```

6. **Run and Install `alterra_bills`**

## Getting Started

### 1. Import Employee Menu

a. Open **Alterra Bills** -> **Import Employee** -> **Import Employee**

b. Before importing, ensure you have opened **Contacts** and selected an active partner, filling in your active email to receive notifications.

c. Choose the file to upload (`xlsx` format, use `setup/hr.employee.xlsx` or `setup/hr.employee small.xlsx` as a sample).

d. Click **Import**. The process will run in the background.

e. You will receive an email notification based on the import status.

### 2. API Authentication

a. Before making requests, import the **Postman Collection** and environment from the `setup/` folder.

b. To log in to the database, use the **Auth/Auth** endpoint with the following JSON request format:
   ```json
   {
       "jsonrpc": "2.0",
       "params": {
           "db": "alterra",
           "login": "api_dev",
           "password": "apidev2024"
       }
   }
   ```
   - `db`: Active Database
   - For login, you can use:
     - `login`: `api_dev`, `password`: `apidev2024`
     - or
     - `login`: `api_bot`, `password`: `api2024`

   Click **Send** (right top blue button) to authenticate. (Dont forget to choose your environment on right top corner.)

c. Use **Auth/Destroy** for logout.

d. Check the response for every successful request.

### 3. Invoice Endpoint

a. **Invoice/Invoice List**: Retrieve a list of invoices.
   
b. **Invoice/Invoice Create**: Create a single invoice.

c. **Invoice/Invoice Create Bulk**: Create multiple invoices.

d. **Invoice/Invoice Update**: Update a single invoice.

e. **Payment/Payment List**: Retrieve a list of payments.

f. **Payment/Payment Register**: Register payment for a single invoice.

g. **Payment/Payment Register Bulk**: Register payments for multiple invoices (one payment per invoice).

h. **Payment/Payment Register Merge**: Register payments for multiple invoices combined into one payment.

   - Optional variables will be marked with `//optional` in the request box.

### Note

If you encounter any issues or have questions, feel free to contact us via email at [billyalvinhartono@gmail.com](mailto:billyalvinhartono@gmail.com).

---

Feel free to adjust the `readme.md` further to include additional details or specific instructions based on your implementation.
