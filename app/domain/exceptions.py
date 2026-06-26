class PipelineError(Exception):
    status_code = 500
    error_code = "PIPELINE_ERROR"


class PipelineRequestNotFoundError(PipelineError):
    status_code = 404
    error_code = "PIPELINE_REQUEST_NOT_FOUND"


class PipelineRunNotFoundError(PipelineError):
    status_code = 404
    error_code = "PIPELINE_RUN_NOT_FOUND"


class InactiveSourceError(PipelineError):
    status_code = 422
    error_code = "INACTIVE_SOURCE"


class InactiveKeywordError(PipelineError):
    status_code = 422
    error_code = "INACTIVE_KEYWORD"


class InvalidRequestStatusError(PipelineError):
    status_code = 409
    error_code = "INVALID_REQUEST_STATUS"


class PipelineAlreadyRunningError(PipelineError):
    status_code = 409
    error_code = "PIPELINE_ALREADY_RUNNING"


class InvalidRunResultError(PipelineError):
    status_code = 422
    error_code = "INVALID_RUN_RESULT"


class RetryNotAllowedError(PipelineError):
    status_code = 409
    error_code = "RETRY_NOT_ALLOWED"


class CancelNotAllowedError(PipelineError):
    status_code = 409
    error_code = "CANCEL_NOT_ALLOWED"
