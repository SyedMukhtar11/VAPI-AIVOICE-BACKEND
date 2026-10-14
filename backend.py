from database import init_db,Appointment,get_db
from sqlalchemy.orm import Session
init_db()
import datetime as dt
from pydantic import BaseModel
class AppointmentRequest(BaseModel):
    patient_name:str
    reason:str
    start_time:dt.datetime

class CancelAppointmentResponse(BaseModel):
    cancel_count:int
class AppointmentResponse(BaseModel):
    id:int
    patient_name:str
    reason : str | None
    start_time : dt.datetime
    cancelled : bool
    created_at : dt.datetime
class CancelAppointmentRequest(BaseModel):
        patient_name:str
        date:dt.date


from fastapi import  FastAPI,HTTPException,Depends
app=FastAPI()
@app.post("/schedule_appointment/")
def schedule_appointment(request:AppointmentRequest,db:Session=Depends(get_db)):
    new_appointment= Appointment(
         patient_name=request.patient_name,
         reason=request.reason,
         start_time=request.start_time
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    new_appointment_return_obj=AppointmentResponse(
         new_appointment.id,
         new_appointment.patient_name,
         new_appointment.reason,
         new_appointment.start_time,
         new_appointment.canceled,
         new_appointment.created_at
         
    )
    return new_appointment_return_obj
from sqlalchemy import select
@app.post("/cancel_appointment/")
def cancel_appointment(request:CancelAppointmentRequest,db:Session=Depends(get_db)):
        start_dt=dt.datetime.combine(request.date,dt.time.min)
        end_dt=start_dt + dt.timedelta(days=1)
        result=db.execute(
             select(Appointment)
             .where(Appointment.patient_name==request.patient_name)
             .where(Appointment.start_time >= start_dt)
             .where(Appointment.end_time<= end_dt)
             .where(Appointment.canceled==False)
        )
        appointments=result.scalars().all()
        if not appointments:
             return HTTPException(status_code=404,detail="No Matching Record")
        for a in appointments:
             a.canceled==True
        db.commit()
        return CancelAppointmentResponse(cancel_count=len(appointments))
     

@app.post("/list_appointment/")
def list_appointment(request:AppointmentRequest,db:Session=Depends(get_db)):
                 start_dt=dt.datetime.combine(request.date,dt.time.min)
                 end_dt=start_dt + dt.timedelta(days=1)
                 result=db.execute(
                                    select(Appointment)
                                    .where(Appointment.patient_name==request.patient_name)
                                    .where(Appointment.start_time >= start_dt)
                                    .where(Appointment.end_time<= end_dt)
                                    .order_by(Appointment.start_time.asc())

                 )
                 booked_appointments=[]
                 for appointment in result:
                                        appointment_obj=AppointmentResponse(
                                                appointment.id,
                                                appointment.patient_name,
                                                appointment.reason,
                                                appointment.start_time,
                                                appointment.canceled,
                                                appointment.created_at
                        
                                            )
                                        appointment_obj.append(booked_appointments)
                 return booked_appointments
import uvicorn
if __name__ == "__main__":
    # "backend:app" refers to: file_name:variable_name
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)