/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SkillOut } from '../models/SkillOut';
import type { SkillsOut } from '../models/SkillsOut';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class SkillsService {

    /**
     * Read Skills
     * Retrieve skills.
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

}
