from datetime import datetime, timedelta 
import json

def initialize_vars():
    # In this function we will declare and initialize variables as well as we will call check_reorderTime() and calculate_job_order()

    global jobs, machine, operation, priority, sequence, job_order, no_of_jobs,desired_endtime, penalty, available_job, available_machine, penalty_imposed, machine_downtime, plant_downtime, operator_downtime, operator, available_operator, fixture,available_fixture, result, totalTime
    
    jobs = [1,2,3]
    machine = [1,2,3,4,5,6,7]
    priority = {1:10,3:10,2:0} #{jobId:priority}
    penalty = {1:True, 3:True}           #{jobId:True/False}
    desired_endtime = {1:"29 02 2024 22:00:00", 3:"03 03 2024 12:00:00"}    #{jobId:desired time}
    operation = {1:{1:8965,2:7896,3:4567},2:{1:895,2:986, 3:86,6:456},3:{4:89,5:78,1:45,2:86}, 6:{1:99,2:48,7:55, 3:95}, 7:{1:109,2:38,3:15,7:567}}       #{jobId:{machineId:operationId,.. }..}
    sequence = {1:[1,2,3], 2:[3,2,1,6], 3:[2,[1,4],5], 5:[1,5,3], 6:[2,[1,3],7], 7:[7,[3,2],1]}        #{jobId:[machine1, machine2....]}
    no_of_jobs = {1:200, 2:180, 3:150}       # {jobid: no of jobs to be perform}
    
    job_details = {5:{"available quantity":50, "minimum quantity":20, "maximum quantity":100}, 
                   6:{"available quantity":10, "minimum quantity":25, "maximum quantity":100, "priority":4, "duedate":"05 03 2024 12:00:00", "penalty":True},
                   7:{"available quantity":10, "minimum quantity":25, "maximum quantity":150 }}
    # job_details = {jobid:{"av quan":0, "min quan": 0, "max quan":0, "priority":0, "duedate":datetime, "penalty":True/False},.....}

    check_reorderTime(job_details)
    
    available_job = {1:"26 02 2024 12:00:00", 2: "26 02 2024 14:00:00", 3: "26 02 2024 16:00:00", 6:"27 02 2024 16:00:00", 7:"29 02 2024 16:00:00"}     #{JobId: available_time}
    available_machine = {1: "26 02 2024 12:00:00", 2:"26 02 2024 12:00:00", 3:"26 02 2024 12:00:00", 
                         4:"26 02 2024 12:00:00", 5:"26 02 2024 12:00:00", 6:"26 02 2024 12:00:00", 7:"26 02 2024 12:00:00"} #{machineId: available_time}
    penalty_imposed = {}   #{jobId:cost}
    machine_downtime = {1:{"starttime":"28 02 2024 12:00:00", "endtime":"28 02 2024 15:00:00"}, 
                        2: {"starttime":"29 02 2024 14:00:00", "endtime":"01 03 2024 01:00:00"},
                        3:{"starttime":"27 02 2024 12:00:00", "endtime":"28 02 2024 08:00:00"}}  #{machineId:{"Starttime":10, "endtime": 20}...}
    plant_downtime = [{"break starttime": "28 02 2024 17:00:00", "break endtime": "28 02 2024 18:00:00", "holiday": ["28 02 2024"],"power down starttime": "28 02 2024 16:00:00", "power down endtime": "28 02 2024 17:30:00"},
                      {"break starttime": "03 03 2024 12:00:00", "break endtime": "03 03 2024 13:00:00", "power down starttime": "03 03 2024 12:00:00", "power down endtime": "03 03 2024 16:00:00"},
                      {"break starttime": "01 03 2024 19:00:00", "break endtime": "01 03 2024 21:00:00", "holiday": ["01 03 2024"]}]  #[{"breakstarttime":10, "breakendtime":20, "holidaystart": 45,"holidayend":56, "powerfailurestart":23, "powerend": 56}...]    
    operator_downtime = {11:{"startdate":"28 02 2024 18:00:00", "enddate":"29 02 2024 15:00:00"}, 
                         87:{"startdate":"27 02 2024 18:00:00", "enddate":"27 02 2024 23:00:00"},
                         111:{"startdate":"29 02 2024 15:00:00", "enddate":"01 03 2024 12:00:00"}}  #{operatorId:{"startdate":12, "enddate":14}...}
    operator = {1:[11,87], 2:87, 3:[111,11], 4:222, 5:[111,222], 6:[87,11],7:87}          #{machineId:operatorId}
    available_operator = {11:"26 02 2024 14:00:00",87:"26 02 2024 12:00:00",111:"26 02 2024 12:00:00", 222: "26 02 2024 12:00:00"}  #     {operatorId:available_time}
    fixture = {1:[97,95], 2:97, 3:[12,15,18], 4:97, 5:[12,95], 6:15, 7:[12,18]}     #{machineId:fixtureId}
    available_fixture = {12:["26 02 2024 01:00:00", "26 02 2024 08:00:00"], 15:"26 02 2024 14:00:00",18:"26 02 2024 18:00:00",
                         45:"26 02 2024 13:00:00",95:"26 02 2024 12:00:00",97:["28 02 2024 15:00:00", "27 02 2024 15:00:00", "26 02 2024 15:00:00"]}  #{fixtureId:Time}  Need to discuss and develop accordingly
    result = []
    totalTime ={1:{1:96300, 2:89452, 3:45789}, 2:{1:66300, 2:75452, 3:59789, 6:65789}, 3:{1:46300, 2:79452, 4:55789, 5:65789}, 
                5:{1:46300, 2:79452, 3:55789}, 6:{1:48300, 2:69452, 3:65789, 7:75789},7:{1:86300, 2:70452, 3:55789, 7:65789}}  #{jobid:{machineid:time}}
    job_order = calculate_job_order(priority,desired_endtime, penalty)


def check_reorderTime(jobDetails):
    ''' In this we will check the quantity available of specific product and if the quantity is 
    below the specific quantity then we have schedule the job according to desired stock 
    as well as we will update job, priority, penalty variables'''
    for jid in jobDetails:
        availableQuantity = jobDetails[jid]["available quantity"]
        minRequiredQuantity = jobDetails[jid]["minimum quantity"]
        if availableQuantity <= minRequiredQuantity:
            jobs.append(jid)
            maximumQuantity = jobDetails[jid]["maximum quantity"]
            nooftasks = maximumQuantity-availableQuantity
            no_of_jobs.update({jid:nooftasks})
            priority.update({jid:jobDetails[jid].get("priority", 0)})
            penalty.update({jid:jobDetails[jid].get("penalty", False)})
            duedate = jobDetails[jid].get("duedate","no key")
            if "no key" not in duedate:
                desired_endtime.update({jid:duedate})


def calculate_job_order(priority, desired_endate, penalty):
    # In this function we will create a sequence list in which a job will we execute on the basis of penalty, highest priority and minimum/smallest due date
    
    sorted_jobs = sorted(priority.keys(), key=lambda x: (
        -penalty.get(x, False),
        -priority.get(x),  # Sort priority in descending order
        datetime.strptime(desired_endate.get(x, "31 12 9999 23:59:59"), "%d %m %Y %H:%M:%S"),
      #  -penalty.get(x,0)
    ))
    return sorted_jobs


def check_job_available(startTime, jobId):
    # In this we will check whether the job is available at a given time or not
    if startTime>=available_job.get(jobId):
        return True
    else:
        return False
    

def check_machine_available(startTime, machineId):
    # In this we have check the available time of machine
    start_time = datetime.strptime(startTime, "%d %m %Y %H:%M:%S")
    machine_availability = datetime.strptime(available_machine.get(machineId), "%d %m %Y %H:%M:%S")
    if start_time >= machine_availability:
        return start_time.strftime("%d %m %Y %H:%M:%S")
    else:
        print(f"Machine {machineId} is not available at {startTime}. Available from: {machine_availability}")       
        return machine_availability.strftime("%d %m %Y %H:%M:%S")
    

def check_operator_available(startTime, operatorId):
    # In this we have check the available time of operator
    start_time = datetime.strptime(startTime, "%d %m %Y %H:%M:%S")
    operator_availability = datetime.strptime(available_operator.get(operatorId), "%d %m %Y %H:%M:%S")
    if start_time >= operator_availability:
        return start_time     
    else:
        print(f"Operator {operatorId} is not available at {start_time}. Available from: {operator_availability}")
        return operator_availability
    

def check_fixture_available(startTime, fixtureId):
    # In this we have check the available time of fixture
    min_av_time = 0
    start_time = datetime.strptime(startTime, "%d %m %Y %H:%M:%S")
    avtime = available_fixture.get(fixtureId)
    if isinstance(avtime,list):
        min_av_time = min(avtime)
    else:
        min_av_time = avtime
    fixture_availability = datetime.strptime(min_av_time, "%d %m %Y %H:%M:%S")
    if start_time >= fixture_availability:
        return start_time
    else:
        return fixture_availability
    

def update_fixture_availabiity(machineId, endTime):
    # In this we will update the available time of fixture with respect to machineid
    fixtureId = fixture.get(machineId)
    if isinstance(fixtureId, list):
        for fid in fixtureId:
            avtime = available_fixture.get(fid)
            if isinstance(avtime,list):
                min_av_time = min(avtime)
                min_av_time_index = available_fixture[fid].index(min_av_time)
                available_fixture[fid][min_av_time_index] = endTime
                print(available_fixture[fid][min_av_time_index], min_av_time_index)
            else:
                available_fixture.update({fid:endTime})
            
            print(fid,":",endTime)                 
    else:
        avtime = available_fixture.get(fixtureId)
        if isinstance(avtime,list):
            min_av_time = min(avtime)
            min_av_time_index = available_fixture[fixtureId].index(min_av_time)
            available_fixture[fixtureId][min_av_time_index] = endTime
        else:
            available_fixture.update({fixtureId:endTime})
        print(fixtureId,":",endTime)


def check_plant_downtime(startTime):
    # In this we check the plant downtime with respect to startime and update starttime if it is required
    # We are assuming plant downtime data would be provided of whole week on day basis
    start_time = datetime.strptime(startTime, "%d %m %Y %H:%M:%S")
    temp = 0
    for i in range(len(plant_downtime)):
        plant_down = plant_downtime[i]
        breakStartTime = plant_down.get("break starttime")
        breakEndTime = plant_down.get("break endtime")
        powerDownStartTime = plant_down.get("power down starttime")
        powerDownEndTime = plant_down.get("power down endtime")
        
        # check whether the value are None or not
        if breakStartTime is not None and breakEndTime is not None:
            breakStartTime = datetime.strptime(breakStartTime, "%d %m %Y %H:%M:%S")
            breakEndTime = datetime.strptime(breakEndTime, "%d %m %Y %H:%M:%S")
        
        if powerDownStartTime is not None and powerDownEndTime is not None:
            powerDownStartTime = datetime.strptime(powerDownStartTime, "%d %m %Y %H:%M:%S")
            powerDownEndTime = datetime.strptime(powerDownEndTime, "%d %m %Y %H:%M:%S")

        # if starttime comes on holiday then we will update the startime to next date  
        holiday = plant_down.get("holiday")
        if holiday is not None:
            for j in range(len(holiday)):
                holiday_date = datetime.strptime(holiday[j],"%d %m %Y").date()
                if(start_time.date() == holiday_date):
                    start_time += timedelta(days=1)
                    # Set the time to 00:10:00
                    start_time = start_time.replace(hour=0, minute=10, second=0)
                
        # need to develop code regarding if starttime comes in between a holiday
        
        if breakStartTime and breakEndTime is not None:
            if powerDownStartTime and powerDownEndTime is not None:
                if (start_time>breakStartTime and start_time<breakEndTime):
                    if (start_time>powerDownStartTime and start_time<powerDownEndTime):
                        start_time = max(breakEndTime,powerDownEndTime)
                    else:
                        start_time = breakEndTime
                    temp+=1
                    break
                elif(start_time>powerDownStartTime and start_time<powerDownEndTime):
                    start_time = powerDownEndTime
                    temp+=1
                elif start_time == powerDownStartTime:
                    start_time = powerDownEndTime
                    temp+=1
                elif start_time == breakStartTime:
                    start_time = breakEndTime
                    temp+=1
            
            else:
                if (start_time>breakStartTime and start_time<breakEndTime):
                    start_time = breakEndTime
                    temp+=1

                elif start_time == breakStartTime:
                    start_time = breakEndTime
                    temp+=1
        if (temp>0):
            i = len(plant_downtime)
    
    print("plant starttime: ",start_time)    
    return start_time
    
def calculate_plant_downtime(startTime, endTime):
    # In this we calculate the plant downtime and if any condition below satisfy then we will update the endtime accordingly
    start_time = datetime.strptime(startTime, "%d %m %Y %H:%M:%S")
    end_time = datetime.strptime(endTime, "%d %m %Y %H:%M:%S")
    temp = 0
    for i in range(len(plant_downtime)):
        plant_down = plant_downtime[i]
        breakStartTime = plant_down.get("break starttime")
        breakEndTime = plant_down.get("break endtime")
        powerDownStartTime = plant_down.get("power down starttime")
        powerDownEndTime = plant_down.get("power down endtime")

        if breakStartTime is not None and breakEndTime is not None:
            breakStartTime = datetime.strptime(breakStartTime, "%d %m %Y %H:%M:%S")
            breakEndTime = datetime.strptime(breakEndTime, "%d %m %Y %H:%M:%S")
        
        if powerDownStartTime is not None and powerDownEndTime is not None:
            powerDownStartTime = datetime.strptime(powerDownStartTime, "%d %m %Y %H:%M:%S")
            powerDownEndTime = datetime.strptime(powerDownEndTime, "%d %m %Y %H:%M:%S")
        
        # if holiday comes in b/w the starttime and endtime then will we add 24 hours to endtime
        holiday = plant_down.get("holiday")
        if holiday is not None:
            for j in range(len(holiday)):
                holiday_date = datetime.strptime(holiday[j],"%d %m %Y").date()
                if start_time.date() < holiday_date and end_time.date() >= holiday_date:
                # need to develop code how could we add a respective date to enddate
                    end_time += timedelta(hours=24)
        
        if breakStartTime is not None and breakEndTime is not None:
            if powerDownStartTime is not None and powerDownEndTime is not None:
                if end_time > breakStartTime and end_time <= breakEndTime:
                    if end_time > powerDownStartTime and end_time <= powerDownEndTime:
                        start_t = min(breakStartTime, powerDownStartTime)
                        endt = max(breakEndTime, powerDownEndTime)
                        end_time = end_time + (endt - start_t)
                    else:
                        end_time = end_time + (breakEndTime - breakEndTime)
                    temp += 1
                
                elif end_time > powerDownStartTime and end_time <= powerDownEndTime:
                    end_time = end_time + (powerDownEndTime - powerDownStartTime)
                    temp += 1

                elif start_time < breakStartTime and end_time >= breakEndTime:
                    if start_time < powerDownStartTime and end_time >= powerDownEndTime:
                        start_t = min(breakStartTime, powerDownStartTime)
                        end_t = max(breakEndTime, powerDownEndTime)
                        end_time = end_time + (end_t - start_t)
                    else:
                        end_time = end_time + (breakEndTime - breakStartTime)
                    temp += 1
                
                elif start_time < powerDownStartTime and end_time >= powerDownEndTime:
                    end_time = end_time + (powerDownEndTime - powerDownStartTime)
                    temp += 1
            
            else:
                if end_time > breakStartTime and end_time <= breakEndTime:
                    end_time = end_time + (breakEndTime - breakEndTime)
                    temp += 1
                elif start_time < breakStartTime and end_time >= breakEndTime:
                    end_time = end_time + (breakEndTime - breakStartTime)
                    temp += 1
        
        if temp > 0:
            break
    
    print("plant endtime: ",end_time)
    return end_time


def check_downtime(startTime, machineId, operatorId):
    # In this we check the machine and operator downtime with respect to startime and update starttime if it is required
    start_time = datetime.strptime(startTime, "%d %m %Y %H:%M:%S")
    machineStartTime = machine_downtime.get(machineId)
    machineEndTime = machine_downtime.get(machineId)
    operatorStartTime = operator_downtime.get(operatorId)
    operatorEndTime = operator_downtime.get(operatorId)
    
    # None check
    if machineStartTime is not None and machineEndTime is not None:
        machineStartTime = datetime.strptime(machineStartTime.get("starttime"), "%d %m %Y %H:%M:%S")
        machineEndTime = datetime.strptime(machineEndTime.get("endtime"), "%d %m %Y %H:%M:%S")
    
    if operatorStartTime is not None and operatorEndTime is not None:
        operatorStartTime = datetime.strptime(operatorStartTime.get("startdate"), "%d %m %Y %H:%M:%S")
        operatorEndTime = datetime.strptime(operatorEndTime.get("enddate"), "%d %m %Y %H:%M:%S")
    #breakStartTime = datetime.strftime()

    if machineStartTime is not None:
        if operatorStartTime is not None:
            if (start_time>machineStartTime and start_time<machineEndTime):
                if (start_time>operatorStartTime and start_time<operatorEndTime):
                    start_time = max(machineEndTime,operatorEndTime)
                else:
                    start_time = machineEndTime
            
            elif(start_time>operatorStartTime and start_time<operatorEndTime):
                start_time = operatorEndTime
            elif start_time == machineStartTime:
                start_time = machineEndTime
            elif start_time == operatorStartTime:
                start_time = operatorEndTime
        
        else:
            if (start_time>machineStartTime and start_time<machineEndTime):
                start_time = machineEndTime
            elif start_time == machineStartTime:
                start_time = machineEndTime
    
    else:
        if operatorStartTime is not None:
            if(start_time>operatorStartTime and start_time<operatorEndTime):
                start_time = operatorEndTime
            elif start_time == operatorStartTime:
                start_time = operatorEndTime
    
    print("machine starttime: ",start_time)
    return start_time 

def calculate_downtime(startTime, endTime, machineId, operatorId):
    # In this we calculate the machine and operator downtime and if any condition below satisfy then we will update the endtime accordingly
    start_time = datetime.strptime(startTime, "%d %m %Y %H:%M:%S")
    end_time = datetime.strptime(endTime, "%d %m %Y %H:%M:%S")
    machineStartTime = machine_downtime.get(machineId)
    machineEndTime = machine_downtime.get(machineId)
    operatorStartTime = operator_downtime.get(operatorId)
    operatorEndTime = operator_downtime.get(operatorId)
    
    if machineStartTime is not None and machineEndTime is not None:
        machineStartTime = datetime.strptime(machineStartTime.get("starttime"), "%d %m %Y %H:%M:%S")
        machineEndTime = datetime.strptime(machineEndTime.get("endtime"), "%d %m %Y %H:%M:%S")
    
    if operatorStartTime is not None and operatorEndTime is not None:
        operatorStartTime = datetime.strptime(operatorStartTime.get("startdate"), "%d %m %Y %H:%M:%S")
        operatorEndTime = datetime.strptime(operatorEndTime.get("enddate"), "%d %m %Y %H:%M:%S")

    if machineStartTime is not None:
        if operatorStartTime is not None:
            if (end_time>machineStartTime and end_time<=machineEndTime):
                if (end_time>operatorStartTime and end_time<=operatorEndTime):
                    start_t = min(machineStartTime,operatorStartTime)
                    endt = max(machineEndTime,operatorEndTime)
                    end_time = end_time+ (endt - start_t)
                else:
                    end_time = end_time+(machineEndTime-operatorEndTime)

            elif (start_time<machineStartTime and end_time>=machineEndTime):
                if (start_time<operatorStartTime and end_time>=operatorEndTime):
                    start_t = min(machineStartTime,operatorStartTime)
                    end_t = max(machineEndTime,operatorEndTime)
                    end_time = end_time + (end_t-start_t)
                else:
                    end_time = end_time + (machineEndTime-machineStartTime)           
        
        else:
            if (end_time>machineStartTime and end_time<=machineEndTime):
                end_time = end_time+(machineEndTime-operatorEndTime)
            elif (start_time<machineStartTime and end_time>=machineEndTime):
                end_time = end_time + (machineEndTime-machineStartTime)
    
    else:
        if operatorStartTime is not None:
            if(end_time>operatorStartTime and end_time<=operatorEndTime):
                end_time = end_time+(operatorEndTime-operatorStartTime)
            elif (start_time<operatorStartTime and end_time>=operatorEndTime):
                end_time = end_time+(operatorEndTime-operatorStartTime)

    print("machine endtime: ",end_time)
    return end_time


def calculate_time(jobId, machineId, startTime, operationId, operatorId, operationCount):
    # In this we calculate the endtime of a respective job on a machine and also calculate downtime and update endtime
    # Also if a job is complete we will check for penalty

    res = {}
    processing_time = totalTime.get(jobId).get(machineId)
    endTime = converting_secondstodatetime(startTime,processing_time)
    
    downtime_end_time = calculate_downtime(startTime, endTime, machineId, operatorId)
    plant_downtime_end_time = calculate_plant_downtime(startTime, endTime)
    end_time = datetime.strptime(endTime, "%d %m %Y %H:%M:%S")
    
    if end_time < max(downtime_end_time, plant_downtime_end_time):
        downtimeEndTime = downtime_end_time.strftime("%d %m %Y %H:%M:%S")
        plant_downtimeEndTime = plant_downtime_end_time.strftime("%d %m %Y %H:%M:%S")
        # Pass the end time calculated by calculate_downtime to calculate_plant_downtime
        plant_downtime_end_time = calculate_plant_downtime(startTime, downtimeEndTime)
        # Pass the end time calculated by calculate_plant_downtime to calculate_downtime
        downtime_end_time = calculate_downtime(startTime, plant_downtimeEndTime, machineId, operatorId)
        # Choose the end time which is greater
        endTime = max(downtime_end_time, plant_downtime_end_time)
        endTime = endTime.strftime("%d %m %Y %H:%M:%S")

    res.update({"MachineId":machineId, "JobId":jobId, "OperationId":operationId, "StartTime":startTime, "EndTime":endTime})
    print(res)
    result.append(res)

    # update the available time for specific jobid, machineid and operatorid
    available_job.update({jobId:endTime})
    available_machine.update({machineId:endTime})
    available_operator.update({operationId:endTime})
    #available_fixture.update({fixtureId:endTime})
    update_fixture_availabiity(machineId, endTime)

    # check for penalty
    if (len(sequence[jobId])-1 == operationCount):
        check_penalty(jobId,endTime)


def schedule_job():
    # In this we will schedule the job with the availability of machine, fixture and operator 
    # Also check for downtime during the starttime 
    count = 0
    print(job_order)
    for i in range(len(jobs)):
        jobId = job_order[i]
        startTime = available_job.get(jobId)
        operation_sequence = sequence.get(jobId)
        
        for j in range(len(operation_sequence)):
            startTime = available_job.get(jobId)
          #  print("start time: ",startTime)
            machineId = operation_sequence[j]
            if isinstance(machineId, list):
                    available_time = {}
                    for mid in range(len(machineId)):
                        operator_startTime = 0
                        machine_startTime = check_machine_available(startTime, machineId[mid])
                        fixtureId = fixture.get(machineId[mid])

                        if isinstance(fixtureId, list):
                            fixture_available_time = []
                            for fid in range(len(fixtureId)):
                                fixture_avtime = check_fixture_available(machine_startTime, fixtureId[fid])
                                fixture_available_time.append(fixture_avtime)
                                if(fid == len(fixtureId)-1):
                                    machine_startTime = max(fixture_available_time)
                                    # machine_startTime = fixture_available_time.get(fixtureId)
                                    machine_startTime = machine_startTime.strftime("%d %m %Y %H:%M:%S")
                        
                        else:
                            machine_startTime = check_fixture_available(machine_startTime, fixtureId)
                            machine_startTime = machine_startTime.strftime("%d %m %Y %H:%M:%S")
                        
                        operationId = operation[jobId][machineId[mid]]
                        operatorId = operator.get(machineId[mid])
                        
                        if isinstance(operatorId, list):
                            operator_startTimeList = {}
                            for oid in range(len(operatorId)):
                                op_startTime = check_operator_available(machine_startTime, operatorId[oid])
                                operator_startTimeList.update({operatorId[oid]:op_startTime})
                                if(oid == len(operatorId)-1):
                                    operatorId = min(operator_startTimeList, key=operator_startTimeList.get)
                                    operator_startTime = operator_startTimeList.get(operatorId)
                                    operator_startTime = operator_startTime.strftime("%d %m %Y %H:%M:%S")
                        
                        else:
                            operator_startTime = check_operator_available(machine_startTime, operatorId)
                            operator_startTime = operator_startTime.strftime("%d %m %Y %H:%M:%S")
                        
                        down_startTime = check_downtime(operator_startTime,machineId[mid],operatorId)
                        plantdown_startTime = check_plant_downtime(operator_startTime)
                        start_time = datetime.strptime(operator_startTime, "%d %m %Y %H:%M:%S")
                        
                        if start_time < max(down_startTime,plantdown_startTime):
                            downtimeStartTime = down_startTime.strftime("%d %m %Y %H:%M:%S")
                            plant_downtimeStartTime = plantdown_startTime.strftime("%d %m %Y %H:%M:%S")
                        
                            down_startTime = check_downtime(plant_downtimeStartTime,machineId[mid],operatorId)
                            plantdown_startTime = check_plant_downtime(downtimeStartTime)

                            start_time = max(down_startTime, plantdown_startTime)
                            print(start_time)
                        
                        available_time.update({machineId[mid]:start_time})
                        
                        if(mid == len(machineId)-1):
                            print(available_time)
                            min_key = min(available_time, key=available_time.get)
                            minimum_starttime = available_time.get(min_key)
                            machineId = min_key
                            print(machineId,minimum_starttime)
                            # print(type(minimum_starttime))
                            startTime = minimum_starttime.strftime("%d %m %Y %H:%M:%S")

                    #startTime = startTime.strftime("%d %m %Y %H:%M:%S")
                    calculate_time(jobId, machineId, startTime, operationId, operatorId, j)
                    count += 1
                    break
                            
            else:
                startTime = check_machine_available(startTime, machineId)
            #    print("upt time: ",startTime)
                fixtureId = fixture.get(machineId)
                
                if isinstance(fixtureId, list):
                    fixture_available_time = []
                    for fid in range(len(fixtureId)):
                        fixture_avtime = check_fixture_available(startTime, fixtureId[fid])
                        fixture_available_time.append(fixture_avtime)
                        if(fid == len(fixtureId)-1):
                            startTime = max(fixture_available_time)
                            #startTime = fixture_available_time.get(fixtureId)
                            startTime = startTime.strftime("%d %m %Y %H:%M:%S")
                
                else:
                    startTime = check_fixture_available(startTime, fixtureId)
                    startTime = startTime.strftime("%d %m %Y %H:%M:%S")
                
                operationId = operation[jobId][machineId]
                operatorId = operator.get(machineId)
                
                if isinstance(operatorId, list):
                    operator_startTimeList = {}
                    for oid in range(len(operatorId)):
                        op_startTime = check_operator_available(startTime, operatorId[oid])
                        operator_startTimeList.update({operatorId[oid]:op_startTime})
                        if(oid == len(operatorId)-1):
                            operatorId = min(operator_startTimeList, key=operator_startTimeList.get)
                            startTime = operator_startTimeList.get(operatorId)
                            startTime = startTime.strftime("%d %m %Y %H:%M:%S")
                
                else:
                    startTime = check_operator_available(startTime, operatorId)
                    startTime = startTime.strftime("%d %m %Y %H:%M:%S")
            #    print("updated time : ",startTime)
                down_startTime = check_downtime(startTime,machineId,operatorId)
                plantdown_startTime = check_plant_downtime(startTime)
                start_time = datetime.strptime(startTime, "%d %m %Y %H:%M:%S")
                
                if start_time < max(down_startTime,plantdown_startTime):
                    downtimeStartTime = down_startTime.strftime("%d %m %Y %H:%M:%S")
                    plant_downtimeStartTime = plantdown_startTime.strftime("%d %m %Y %H:%M:%S")
                        
                    down_startTime = check_downtime(plant_downtimeStartTime,machineId,operatorId)
                    plantdown_startTime = check_plant_downtime(downtimeStartTime)
                    downtime_startTime = max(down_startTime, plantdown_startTime)
                    startTime = downtime_startTime.strftime("%d %m %Y %H:%M:%S")

                calculate_time(jobId, machineId, startTime, operationId, operatorId, j)
                count += 1
        #print(count)
     
def check_penalty(jobId, endTime):
    # In this we check for penalty whether it will be imposed or not  
    desired_end = desired_endtime.get(jobId)
    if desired_end is not None:
        if endTime <= desired_end:
            print("No penalty")
        else:
            penaltyCost = penalty.get(jobId)
            if penaltyCost and penaltyCost is not None:
                penalty_charged = calculate_penalty(desired_end, endTime)
                print("Penalty charged for JOBID {} is {}".format(jobId, penalty_charged))
                penalty_imposed.update({jobId: penalty_charged})
            else:
                print("Penalty data not available for JobID: ", jobId)
    else:
        print("End time not available for JobID: ", jobId)

def calculate_penalty(desired_endtime, endtime):
    # We calculate penalty for a job and return the penalty in seconds
    actual_endtime = datetime.strptime(endtime, '%d %m %Y %H:%M:%S')
    given_endtime = datetime.strptime(desired_endtime, '%d %m %Y %H:%M:%S')
    penaltyTime = actual_endtime - given_endtime
    if penaltyTime>timedelta(0):
        print(penaltyTime.total_seconds())
      #  penaltyCharged = penalty * penaltyTime.total_seconds()  # Calculating penalty based on total seconds
        return penaltyTime.total_seconds()
    else:
        return 0

def converting_secondstodatetime(startTime, processing_time):
    # We calculate the endtime with respect to starttime and processing_time which is given in seconds
    date_object = datetime.strptime(startTime, '%d %m %Y %H:%M:%S')
    # Add the duration to the datetime object
    updated_date = date_object + timedelta(seconds=processing_time)
    updated_date_string = updated_date.strftime('%d %m %Y %H:%M:%S')
    return updated_date_string


initialize_vars()
schedule_job()
print(result)
# with open("output.json","w") as write_file:
#     json.dump(result, write_file)
print(penalty_imposed)


'''This code was develop before now it is not in use'''
# def add_time_difference(start_time_str, end_time_str, target_time_str):
#     start_time = datetime.strptime(start_time_str, '%d %m %Y %H:%M:%S')
#     end_time = datetime.strptime(end_time_str, '%d %m %Y %H:%M:%S')
#     target_time = datetime.strptime(target_time_str, '%d %m %Y %H:%M:%S')
#     time_difference = end_time - start_time
#     updated_endTime = target_time + time_difference
#     return updated_endTime.strftime('%d %m %Y %H:%M:%S') 


# def calculate_machine_downtime(startTime, endTime, machineId):
#     # In this check downtime of respective machine
#     mach_down = []
#     if endTime>machine_downtime.get(machineId).get("starttime") and endTime<=machine_downtime.get(machineId).get("endtime"):
#         mach_down.append(machine_downtime.get(machineId).get("starttime"))
#         mach_down.append(machine_downtime.get(machineId).get("endtime"))
        
#     elif startTime<=machine_downtime.get(machineId).get("starttime") and endTime>machine_downtime.get(machineId).get("endtime"):
#         mach_down.append(machine_downtime.get(machineId).get("starttime"))
#         mach_down.append(machine_downtime.get(machineId).get("endtime"))
        
#     return mach_down

# def calculate_plant_downtime(startTime, endTime):
#     # need to revise the constraint in plant downtime 
#     # we have to check downtime of plant including holiday, break.
#     plant_down = []
#     for i in range(len(plant_downtime)):
#         if endTime>plant_downtime[i].get("starttime") and endTime<=plant_downtime[i].get("endtime"):
#             plant_down.append(machine_downtime[i].get("starttime"))
#             plant_down.append(machine_downtime[i].get("endtime"))
        
#         elif startTime<=plant_downtime[i].get("starttime") and endTime>plant_downtime[i].get("endtime"):
#             plant_down.append(machine_downtime[i].get("starttime"))
#             plant_down.append(machine_downtime[i].get("endtime"))
#     return plant_down

# def calculate_operator_downtime(startTime, endTime, operatorId):
#     opr_down = []
#     if endTime>operator_downtime.get(operatorId).get("startdate") and endTime<=operator_downtime.get(operatorId).get("enddate"):
#         opr_down.append(operator_downtime.get(operatorId).get("startdate"))
#         opr_down.append(operator_downtime.get(operatorId).get("enddate"))
        
#     elif startTime<=operator_downtime.get(operatorId).get("startdate") and endTime>operator_downtime.get(operatorId).get("enddate"):
#         opr_down.append(operator_downtime.get(operatorId).get("startdate"))
#         opr_down.append(operator_downtime.get(operatorId).get("enddate"))
    
#     return opr_down

# def schedule_job():
#     operations = 40
#     startTime = 0
#     temp = 1
#     count = 1
    
#     for i in range(operations):
#         if i == 0:
#             current_time_seconds = time.time()
#             current_time = time.localtime(current_time_seconds)
#             startTime = time.strftime("%d %m %Y %H:%M:%S", current_time)
        
#         if temp > len(jobs):
#             temp = 1
#             date_times = [datetime.strptime(value, "%d %m %Y %H:%M:%S") for value in available_job.values()]
#             minimumtime = min(date_times) + timedelta(minutes=10)
#             startTime = minimumtime.strftime("%d %m %Y %H:%M:%S") 
        
#         jobId = priority.get(temp)
        
#         if check_job_available(startTime, jobId):
#             machineId_List = sequence.get(jobId)
            
#             if len(machineId_List) < 1:
#                 pass
#             else:
#                 machineId = machineId_List[0]
#                 machineId_List.pop(0)
            
#                 if isinstance(machineId, list):
#                     for mid in range(len(machineId)):
#                         t = count
#                         if check_machine_available(startTime, machineId[mid]):
#                             operationId = operation[jobId][machineId[mid]]
#                             operatorId = operator.get(machineId[mid])
#                             if check_operator_available(startTime, operatorId):
#                                 calcuate_time(jobId, machineId[mid], startTime, operationId, operatorId)
#                                 count += 1
#                                 break
#                             else:
#                                 available_machine.update({machineId[mid]: available_operator.get(machineId[mid])})
#                                 available_job.update({jobId: available_machine.get(machineId)})
#                         if(mid == len(machineId)-1):
#                             available_job.update({jobId: available_machine.get(machineId)})

#                         if t < count:
#                             break
#                 else:
#                     if check_machine_available(startTime, machineId):
#                         operationId = operation[jobId][machineId]
#                         operatorId = operator.get(machineId)
#                         if check_operator_available(startTime, operatorId):
#                             calcuate_time(jobId, machineId, startTime, operationId, operatorId)
#                             count += 1
#                         else:
#                             available_machine.update({machineId: available_operator.get(machineId)})
#                     else:
#                         available_job.update({jobId: available_machine.get(machineId)})
#         else:

#             pass
            
#         temp += 1


# def calculate_time():
    # mach_down = []
    # opr_down = []
    # minimum_startTime = ""
    # maximum_endTime = ""
    # mach_down = calculate_machine_downtime(startTime,endTime,machineId)
    # opr_down = calculate_operator_downtime(startTime,endTime,operatorId)
    # if(len(mach_down)<1):
    #     if(len(opr_down)<1):
    #         print("no downtime")
    #     else:
    #         minimum_startTime = opr_down[0]
    #         maximum_endTime = opr_down[1]
    # elif(len(opr_down)<1):
    #     if(len(mach_down)<1):
    #         print("no downtime")
    #     else: 
    #        maximum_endTime = mach_down[1]
    #        minimum_startTime = mach_down[0] 
    # else:
    #     maximum_endTime = max(opr_down[1],mach_down[1])
    #     minimum_startTime = min([opr_down[0],mach_down[0]])
        #print(minimum_startTime,maximum_endTime)
    
    # if(len(minimum_startTime)>1):
    #     endTime = add_time_difference(minimum_startTime,maximum_endTime,endTime)