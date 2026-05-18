## Setup & Run

**1. Clone the project**
```bash
git clone https://github.com/NiJiSann/AQA_Tets.git
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run tests with Allure results**
```bash
pytest --alluredir=allure-results
```

**4. Generate and serve the report**
```bash
allure serve allure-results
```

---

## SQL Task Solution

```sql
SELECT
    e.Emp_no,
    e.Emp_Name,
    e.Date_start,
    d.Descr
FROM Emp e
JOIN Dep d ON e.Dep = d.No
WHERE e.Emp_no < 1000
```