from crams import models as CramsModels


# create project question response
def create_project_question_response(crams_project, question_key, question_response):
    # if None, convert to empty string
    if question_response is None:
        question_response = ''
    question = CramsModels.Question.objects.get(key=question_key)
    crams_quest_resp = CramsModels.ProjectQuestionResponse()
    crams_quest_resp.question_response = question_response
    crams_quest_resp.project = crams_project
    crams_quest_resp.question = question

    crams_quest_resp.save()


# create request question responses
def create_request_question_response(crams_request, question_key, question_response):
    # if None, convert to empty string
    if question_response is None:
        question_response = ''
    question = CramsModels.Question.objects.get(key=question_key)
    crams_quest_resp = CramsModels.RequestQuestionResponse()
    crams_quest_resp.question_response = question_response
    crams_quest_resp.request = crams_request
    crams_quest_resp.question = question

    crams_quest_resp.save()


# create compute request question responses
def create_compute_request_question_response(crams_comp_req, question_key, question_response):
    # Only save if question_response is not null or empty string
    if question_response and question_response.strip() != '':
        question = CramsModels.Question.objects.get(key=question_key)
        crams_quest_resp = CramsModels.ComputeRequestQuestionResponse()
        crams_quest_resp.question_response = question_response
        crams_quest_resp.compute_request = crams_comp_req
        crams_quest_resp.question = question

        crams_quest_resp.save()


# create storage request question responses
def create_storage_request_question_response(crams_stor_req, question_key, question_response):
    # Only save if question_response is not null or empty string
    if question_response and question_response.strip() != '':
        question = CramsModels.Question.objects.get(key=question_key)
        crams_quest_resp = CramsModels.StorageRequestQuestionResponse()
        crams_quest_resp.question_response = question_response
        crams_quest_resp.storage_request = crams_stor_req
        crams_quest_resp.question = question

        crams_quest_resp.save()
