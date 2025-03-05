import meds_reader

database = meds_reader.SubjectDatabase("data/mimiciv_meds/meds_reader_data")

for subject_id in database:
    # We can retrieve subject data given a subject_id
    subject = database[subject_id]

    # Subject data can be manipulated with normal Python operations
    print(subject.subject_id)
    for event in subject.events:
        print(event.time, event.code)
        if event.code.startswith("HOSPITAL_ADMISSION"):
            for property_name, property_value in event:
                print(property_name, property_value)
        