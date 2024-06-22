/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_uploads_create_upload } from '../models/Body_uploads_create_upload';
import type { Body_uploads_update_upload } from '../models/Body_uploads_update_upload';
import type { Message } from '../models/Message';
import type { UploadOut } from '../models/UploadOut';
import type { UploadsOut } from '../models/UploadsOut';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class UploadsService {

    /**
     * Read Uploads
     * Retrieve uploads.
     * @returns UploadsOut Successful Response
     * @throws ApiError
     */
    public static readUploads({
        skip,
        limit = 100,
    }: {
        skip?: number,
        limit?: number,
    }): CancelablePromise<UploadsOut> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/uploads/',
            query: {
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Upload
     * Create upload
     * @returns UploadOut Successful Response
     * @throws ApiError
     */
    public static createUpload({
        contentLength,
        formData,
    }: {
        contentLength: number,
        formData: Body_uploads_create_upload,
    }): CancelablePromise<UploadOut> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/uploads/',
            headers: {
                'content-length': contentLength,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Upload
     * Update upload
     * @returns UploadOut Successful Response
     * @throws ApiError
     */
    public static updateUpload({
        id,
        contentLength,
        formData,
    }: {
        id: number,
        contentLength: number,
        formData?: Body_uploads_update_upload,
    }): CancelablePromise<UploadOut> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/uploads/{id}',
            path: {
                'id': id,
            },
            headers: {
                'content-length': contentLength,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Upload
     * @returns Message Successful Response
     * @throws ApiError
     */
    public static deleteUpload({
        id,
    }: {
        id: number,
    }): CancelablePromise<Message> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/uploads/{id}',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
