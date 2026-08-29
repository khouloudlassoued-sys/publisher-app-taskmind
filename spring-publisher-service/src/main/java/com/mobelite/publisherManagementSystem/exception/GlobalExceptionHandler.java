package com.mobelite.publisherManagementSystem.exception;
import com.mobelite.publisherManagementSystem.dto.response.ApiResponseDto;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.ConstraintViolationException;
import jakarta.validation.ValidationException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.validation.FieldError;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

/**
 * Global exception handler for the application.
 * Handles various exceptions and returns appropriate error responses.
 */
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(BadCredentialsException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleBadCredentials(BadCredentialsException ex) {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(ApiResponseDto.error("Invalid username or password"));
    }

    /**
     * Handle resource not found exceptions.
     * @param ex The exception
     * @return Error response with NOT_FOUND status
     */
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleResourceNotFoundException(ResourceNotFoundException ex) {
        log.error("Resource not found: {}", ex.getMessage());
        ApiResponseDto<Object> response = ApiResponseDto.error(ex.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(response);
    }

    /**
     * Handle duplicate resource exceptions.
     * @param ex The exception
     * @return Error response with CONFLICT status
     */
    @ExceptionHandler(DuplicateResourceException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleDuplicateResourceException(DuplicateResourceException ex) {
        log.error("Duplicate resource: {}", ex.getMessage());
        ApiResponseDto<Object> response = ApiResponseDto.error(ex.getMessage());
        return ResponseEntity.status(HttpStatus.CONFLICT).body(response);
    }

    /**
     * Handle business rule violations.
     * @param ex The exception
     * @return Error response with BAD_REQUEST status
     */
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleBusinessException(BusinessException ex) {
        log.error("Business rule violation: {}", ex.getMessage());
        ApiResponseDto<Object> response = ApiResponseDto.error(ex.getMessage());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * Handle validation exceptions from @Valid annotation.
     * @param ex The exception
     * @return Error response with validation details
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleValidationExceptions(MethodArgumentNotValidException ex) {
        log.error("Validation error: {}", ex.getMessage());

        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getAllErrors().forEach(error -> {
            String fieldName = ((FieldError) error).getField();
            String errorMessage = error.getDefaultMessage();
            errors.put(fieldName, errorMessage);
        });

        ApiResponseDto<Object> response = ApiResponseDto.<Object>builder()
                .success(false)
                .message("Validation failed")
                .data(errors)
                .timestamp(LocalDateTime.now())
                .build();

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * Handle constraint violations (e.g., @NotNull, @Size, etc.).
     * @param ex The exception
     * @return Error response with constraint violation details
     */
    @ExceptionHandler(ConstraintViolationException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleConstraintViolationException(ConstraintViolationException ex) {
        log.error("Constraint violation: {}", ex.getMessage());

        Map<String, String> errors = new HashMap<>();
        Set<ConstraintViolation<?>> violations = ex.getConstraintViolations();

        for (ConstraintViolation<?> violation : violations) {
            String fieldName = violation.getPropertyPath().toString();
            String errorMessage = violation.getMessage();
            errors.put(fieldName, errorMessage);
        }

        ApiResponseDto<Object> response = ApiResponseDto.<Object>builder()
                .success(false)
                .message("Constraint validation failed")
                .data(errors)
                .timestamp(LocalDateTime.now())
                .build();

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * Handle generic validation exceptions.
     * @param ex The exception
     * @return Error response with BAD_REQUEST status
     */
    @ExceptionHandler(ValidationException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleValidationException(ValidationException ex) {
        log.error("Validation error: {}", ex.getMessage());
        ApiResponseDto<Object> response = ApiResponseDto.error(ex.getMessage());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * Handle data integrity violations (database constraints).
     * @param ex The exception
     * @return Error response with CONFLICT status
     */
    @ExceptionHandler(DataIntegrityViolationException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleDataIntegrityViolation(DataIntegrityViolationException ex) {
        log.error("Data integrity violation: {}", ex.getMessage());

        String message = "Database constraint violation";
        String errorMessage = ex.getMessage().toLowerCase();

         if (errorMessage.contains("unique")) {
            message = "Duplicate value for unique field";
        }

        ApiResponseDto<Object> response = ApiResponseDto.error(message);
        return ResponseEntity.status(HttpStatus.CONFLICT).body(response);
    }

    /**
     * Handle malformed JSON requests.
     * @param ex The exception
     * @return Error response with BAD_REQUEST status
     */
    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleHttpMessageNotReadable(HttpMessageNotReadableException ex) {
        log.error("Malformed JSON request: {}", ex.getMessage());
        ApiResponseDto<Object> response = ApiResponseDto.error("Invalid JSON format");
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * Handle unsupported HTTP methods.
     * @param ex The exception
     * @return Error response with METHOD_NOT_ALLOWED status
     */
    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleHttpRequestMethodNotSupported(HttpRequestMethodNotSupportedException ex) {
        log.error("Method not supported: {}", ex.getMessage());
        String message = String.format("Method '%s' not supported. Supported methods: %s",
                ex.getMethod(), String.join(", ", ex.getSupportedMethods()));
        ApiResponseDto<Object> response = ApiResponseDto.error(message);
        return ResponseEntity.status(HttpStatus.METHOD_NOT_ALLOWED).body(response);
    }

    /**
     * Handle missing request parameters.
     * @param ex The exception
     * @return Error response with BAD_REQUEST status
     */
    @ExceptionHandler(MissingServletRequestParameterException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleMissingServletRequestParameter(MissingServletRequestParameterException ex) {
        log.error("Missing request parameter: {}", ex.getMessage());
        String message = String.format("Required parameter '%s' is missing", ex.getParameterName());
        ApiResponseDto<Object> response = ApiResponseDto.error(message);
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * Handle method argument type mismatches.
     * @param ex The exception
     * @return Error response with BAD_REQUEST status
     */
    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleMethodArgumentTypeMismatch(MethodArgumentTypeMismatchException ex) {
        log.error("Method argument type mismatch: {}", ex.getMessage());
        String message = String.format("Invalid value '%s' for parameter '%s'. Expected type: %s",
                ex.getValue(), ex.getName(), ex.getRequiredType().getSimpleName());
        ApiResponseDto<Object> response = ApiResponseDto.error(message);
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * Handle generic exceptions as fallback.
     * @param ex The exception
     * @return Error response with INTERNAL_SERVER_ERROR status
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponseDto<Object>> handleGenericException(Exception ex) {
        log.error("Unexpected error: {}", ex.getMessage(), ex);
        ApiResponseDto<Object> response = ApiResponseDto.error("An unexpected error occurred");
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
    }
}