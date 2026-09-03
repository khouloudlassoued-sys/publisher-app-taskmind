import { Inject, Injectable, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Router } from '@angular/router';
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { environment } from '../../../environments/environment';
import { LoaderService } from './loader.service';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private axiosInstance: AxiosInstance;

  constructor(private loader: LoaderService, private router: Router, @Inject(PLATFORM_ID) private platformId: object) {
    console.log('API Base URL:', environment.apiBaseUrl); // Debug log for base URL
    this.axiosInstance = axios.create({
      baseURL: environment.apiBaseUrl,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Attach interceptors to manage loader state
    this.axiosInstance.interceptors.request.use((config) => {
      this.loader.start();
      if (isPlatformBrowser(this.platformId) && !config.url?.includes('/auth/login')) {
        const token = localStorage.getItem('admin_access_token');
        if (token) config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    }, (error) => {
      this.loader.stop();
      return Promise.reject(error);
    });

    this.axiosInstance.interceptors.response.use((response) => {
      this.loader.stop();
      return response;
    }, (error) => {
      this.loader.stop();
      if (error.response?.status === 401 && isPlatformBrowser(this.platformId)) {
        localStorage.removeItem('admin_access_token');
        void this.router.navigate(['/admin/login'], { queryParams: { returnUrl: this.router.url } });
      }
      return Promise.reject(error);
    });
  }

  public get<T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.axiosInstance.get<T>(url, config).catch(this.handleError);
  }

  public post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.axiosInstance.post<T>(url, data, config).catch(this.handleError);
  }

  public put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.axiosInstance.put<T>(url, data, config).catch(this.handleError);
  }

  public delete<T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.axiosInstance.delete<T>(url, config).catch(this.handleError);
  }
  
  private handleError(error: any): never {
    throw error;
  }
} 