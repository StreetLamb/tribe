/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SkillCreate } from '../models/SkillCreate';
import type { SkillOut } from '../models/SkillOut';
import type { SkillsOut } from '../models/SkillsOut';
import type { SkillUpdate } from '../models/SkillUpdate';
import type { ToolDefinitionValidate } from '../models/ToolDefinitionValidate';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class SkillsService {

    /**
     * Read Skills
     * Retrieve skills
     * @returns SkillsOut Successful Response
     * @throws ApiError
     */
    public static readSkills({
        skip,
        limit = 100,
    }: {
        skip?: number,
        limit?: number,
    }): CancelablePromise<SkillsOut> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/skills/',
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
     * Create Skill
     * Create new skill.
     * @returns SkillOut Successful Response
     * @throws ApiError
     */
    public static createSkill({
        requestBody,
    }: {
        requestBody: SkillCreate,
    }): CancelablePromise<SkillOut> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/skills/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Read Skill
     * Get skill by ID.
     * @returns SkillOut Successful Response
     * @throws ApiError
     */
    public static readSkill({
        id,
    }: {
        id: number,
    }): CancelablePromise<SkillOut> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/skills/{id}',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Skill
     * Update a skill.
     * @returns SkillOut Successful Response
     * @throws ApiError
     */
    public static updateSkill({
        id,
        requestBody,
    }: {
        id: number,
        requestBody: SkillUpdate,
    }): CancelablePromise<SkillOut> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/skills/{id}',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Skill
     * Delete a skill.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteSkill({
        id,
    }: {
        id: number,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/skills/{id}',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Validate Skill
     * Validate skill's tool definition.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static validateSkill({
        requestBody,
    }: {
        requestBody: ToolDefinitionValidate,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/skills/validate',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
