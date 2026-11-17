import { apiClient } from './client'
import type {
  AreaProgressItem,
  DashboardProgressResponse,
  WeeklyAssessment,
  WeeklyAssessmentCreate,
} from '../types/progress'

export async function fetchDashboardProgress(): Promise<DashboardProgressResponse> {
  const res = await apiClient.get<DashboardProgressResponse>('/progress/dashboard')
  return res.data
}

export async function fetchAreasProgress(): Promise<AreaProgressItem[]> {
  const res = await apiClient.get<AreaProgressItem[]>('/progress/areas')
  return res.data
}

export async function fetchLatestAssessment(): Promise<WeeklyAssessment | null> {
  const res = await apiClient.get<WeeklyAssessment | null>('/assessment/latest')
  return res.data
}

export async function saveWeeklyAssessmentApi(
  payload: WeeklyAssessmentCreate
): Promise<WeeklyAssessment> {
  const res = await apiClient.post<WeeklyAssessment>('/assessment', payload)
  return res.data
}

export async function generateWeeklyReportApi(assessmentId: number): Promise<WeeklyAssessment> {
  const res = await apiClient.post<WeeklyAssessment>(`/assessment/${assessmentId}/generate-report`)
  return res.data
}
