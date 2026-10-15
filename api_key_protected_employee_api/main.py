from fastapi import FastAPI,HTTPException,Depends, Header
import secrets
import os
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr, Field
from supabase import create_client, Client
load_dotenv()

app = FastAPI()

SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
client = create_client(SUPABASE_URL,SUPABASE_KEY)
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise RuntimeError("API_KEY is not configured")


class Employee(BaseModel):
    emp_id:int
    emp_name: str = Field(min_length=1, max_length=100)
    dept: str = Field(min_length=1, max_length=100)
    role: str = Field(min_length=1, max_length=100)

@app.post("/employees")
def create_employee(employee: Employee):
    check_emp_record_exists = client.table("employees").select("*").eq("emp_id",employee.emp_id).execute()

    if check_emp_record_exists.data:
        raise HTTPException(
            status_code=409,
            detail="employee with same id is already exists"
        )
    else :
        response = client.table("employees").insert(employee.dict()).execute()
    return response.data

@app.get("/employees")
def get_employees():
    response = client.table("employees").select("*").execute()
    return response.data

def verify_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key")
):
    if x_api_key is None:
        raise HTTPException(
            status_code=401,
            detail="API key is missing"
        )

    if not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    return True

class Update_Employee(BaseModel):
    emp_id:int
    emp_name: str = Field(min_length=1, max_length=100)
    dept: str = Field(min_length=1, max_length=100)
    role: str = Field(min_length=1, max_length=100)

@app.put("/employees/{employee_id}")
def update_employee_record(employee:Update_Employee, employee_id:int,_: bool = Depends(verify_api_key)):
    check_employee_id_exists = client.table("employees").select("*").eq("emp_id",employee_id).execute()

    if not check_employee_id_exists.data:
        raise HTTPException(
            status_code=404,
            detail="emp_id is not found"
        )
    else:
        response = client.table("employees").update(employee.model_dump()).eq("emp_id",employee.emp_id).execute()
    return response.data

@app.delete("/employees/{employee_id}")
def delete_employee_record(employee_id:int, _: bool = Depends(verify_api_key)):
    check_employee_id_exists = client.table("employees").select("*").eq("emp_id",employee_id).execute()
    
    if not check_employee_id_exists.data:
        raise HTTPException(
            status_code=404,
            detail="emp_id is not found"
        )
    else:
        response = client.table("employees").delete().eq("emp_id",employee_id).execute()
        return {"data":response.data,
                "message" : "successfully deleted the record"
        }








