import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useToast } from "hooks/use-toast";
import { 
  Download, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  RefreshCw,
  FileText,
  BookOpen,
  BarChart3,
  Star,
  Users,
  Target,
  ArrowLeft,
  ExternalLink
} from 'lucide-react'

const ResultsPage = () => {
  const { taskId } = useParams()
  const { toast } = useToast()
  
  const [taskData, setTaskData] = useState(null)
  const [taskType, setTaskType] = useState(null) // 'analysis' or 'generation'
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  // 작업 상태 폴링
  useEffect(() => {
    if (!taskId) return

    const checkTaskStatus = async () => {
      try {
        // 먼저 분석 작업인지 확인
        let response = await fetch(`/api/v1/books/analyze/${taskId}/status`)
        
        if (response.ok) {
          setTaskType('analysis')
          const data = await response.json()
          setTaskData(data)
          setIsLoading(false)
          return
        }

        // 분석 작업이 아니면 문서 생성 작업인지 확인
        response = await fetch(`/api/v1/documents/${taskId}/status`)
        
        if (response.ok) {
          setTaskType('generation')
          const data = await response.json()
          setTaskData(data)
          setIsLoading(false)
          return
        }

        throw new Error('작업을 찾을 수 없습니다.')

      } catch (err) {
        console.error('Status check error:', err)
        setError(err.message)
        setIsLoading(false)
      }
    }

    // 초기 상태 확인
    checkTaskStatus()

    // 작업이 완료되지 않은 경우 주기적으로 상태 확인
    const interval = setInterval(() => {
      if (taskData?.status === 'completed' || taskData?.status === 'failed') {
        clearInterval(interval)
        return
      }
      checkTaskStatus()
    }, 2000)

    return () => clearInterval(interval)
  }, [taskId, taskData?.status])

  const handleDownload = async (type) => {
    try {
      let url
      let filename
      
      if (type === 'csv' && taskType === 'analysis') {
        url = `/api/v1/books/analyze/${taskId}/csv`
        filename = `analysis_${taskId}.csv`
      } else if (type === 'docx' && taskType === 'generation') {
        url = `/api/v1/documents/${taskId}/download`
        filename = `textbook_${taskId}.docx`
      } else {
        throw new Error('잘못된 다운로드 요청입니다.')
      }

      const response = await fetch(url)
      if (!response.ok) {
        throw new Error('다운로드에 실패했습니다.')
      }

      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)

      toast({
        title: "다운로드 완료",
        description: `${filename} 파일이 다운로드되었습니다.`
      })

    } catch (error) {
      console.error('Download error:', error)
      toast({
        title: "다운로드 실패",
        description: error.message,
        variant: "destructive"
      })
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />
      case 'processing':
        return <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />
      default:
        return <Clock className="h-5 w-5 text-yellow-500" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'processing':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      default:
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    }
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center space-y-4">
              <RefreshCw className="h-8 w-8 text-blue-500 animate-spin mx-auto" />
              <p className="text-gray-600">작업 상태를 확인하는 중...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card className="border-red-200">
          <CardContent className="text-center py-12">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-red-800 mb-2">오류 발생</h2>
            <p className="text-red-600 mb-4">{error}</p>
            <div className="space-x-4">
              <Link to="/">
                <Button variant="outline">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  홈으로 돌아가기
                </Button>
              </Link>
              <Button onClick={() => window.location.reload()}>
                <RefreshCw className="h-4 w-4 mr-2" />
                다시 시도
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-gray-900">
            {taskType === 'analysis' ? '원서 분석 결과' : '교재 생성 결과'}
          </h1>
          <p className="text-gray-600">
            작업 ID: {taskId}
          </p>
        </div>
        <Link to={taskType === 'analysis' ? '/analyze' : '/generate'}>
          <Button variant="outline">
            <ArrowLeft className="h-4 w-4 mr-2" />
            돌아가기
          </Button>
        </Link>
      </div>

      {/* 상태 카드 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            {getStatusIcon(taskData.status)}
            <span>작업 상태</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Badge className={`${getStatusColor(taskData.status)} border`}>
              {taskData.status === 'completed' && '완료'}
              {taskData.status === 'failed' && '실패'}
              {taskData.status === 'processing' && '진행 중'}
              {taskData.status === 'pending' && '대기 중'}
            </Badge>
            <span className="text-sm text-gray-500">
              {Math.round(taskData.progress * 100)}% 완료
            </span>
          </div>
          
          <Progress value={taskData.progress * 100} className="w-full" />
          
          <p className="text-sm text-gray-600">{taskData.message}</p>
        </CardContent>
      </Card>

      {/* 결과 내용 */}
      {taskData.status === 'completed' && (
        <>
          {taskType === 'analysis' && taskData.result && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 분석 요약 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <BarChart3 className="h-5 w-5 text-blue-500" />
                    <span>분석 요약</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {taskData.result.overall_score.toFixed(1)}
                      </div>
                      <div className="text-sm text-gray-600">전체 점수</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {taskData.result.topics_generated}
                      </div>
                      <div className="text-sm text-gray-600">생성된 주제</div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-2">우수 영역</h4>
                    <div className="space-y-1">
                      {taskData.result.best_areas.map((area, index) => (
                        <Badge key={index} variant="secondary" className="mr-2">
                          {area}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* 도서 정보 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <BookOpen className="h-5 w-5 text-purple-500" />
                    <span>도서 정보</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <div className="font-semibold">{taskData.result.book_info.title}</div>
                    <div className="text-sm text-gray-600">{taskData.result.book_info.author}</div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">AR 레벨</span>
                    <Badge variant="outline">{taskData.result.book_info.ar_level}</Badge>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">교육 레벨</span>
                    <Badge variant="outline">
                      {taskData.result.book_info.education_level}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* 다운로드 섹션 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Download className="h-5 w-5 text-green-500" />
                <span>다운로드</span>
              </CardTitle>
              <CardDescription>
                {taskType === 'analysis' 
                  ? '분석 결과를 CSV 파일로 다운로드하거나 교재 생성으로 진행하세요.'
                  : '생성된 DOCX 교재를 다운로드하세요.'
                }
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col sm:flex-row gap-4">
                {taskType === 'analysis' ? (
                  <>
                    <Button 
                      onClick={() => handleDownload('csv')}
                      className="flex-1"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      CSV 다운로드
                    </Button>
                    <Link to="/generate" className="flex-1">
                      <Button variant="outline" className="w-full">
                        <FileText className="h-4 w-4 mr-2" />
                        교재 생성하기
                        <ExternalLink className="h-4 w-4 ml-2" />
                      </Button>
                    </Link>
                  </>
                ) : (
                  <Button 
                    onClick={() => handleDownload('docx')}
                    className="flex-1 bg-green-600 hover:bg-green-700"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    DOCX 교재 다운로드
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* 다음 단계 안내 */}
          <Card className="bg-blue-50 border-blue-200">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-blue-800">
                <Target className="h-5 w-5" />
                <span>다음 단계</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="text-blue-700">
              {taskType === 'analysis' ? (
                <div className="space-y-2">
                  <p>✅ 원서 분석이 완료되었습니다!</p>
                  <p>📝 이제 CSV 파일을 다운로드하여 교재 생성 단계로 진행하세요.</p>
                  <p>🎯 생성된 토론 주제들을 검토하고 필요에 따라 수정할 수 있습니다.</p>
                </div>
              ) : (
                <div className="space-y-2">
                  <p>✅ 교재 생성이 완료되었습니다!</p>
                  <p>📖 DOCX 파일을 다운로드하여 바로 수업에 활용하세요.</p>
                  <p>🎓 학습자 레벨에 맞는 완전한 토론 교재가 준비되었습니다.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* 실패 시 안내 */}
      {taskData.status === 'failed' && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-red-800">
              <AlertCircle className="h-5 w-5" />
              <span>작업 실패</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="text-red-700">
            <p className="mb-4">{taskData.message}</p>
            <div className="space-y-2 text-sm">
              <p>• 입력 데이터를 다시 확인해주세요</p>
              <p>• 네트워크 연결 상태를 확인해주세요</p>
              <p>• 문제가 지속되면 고객지원팀에 문의해주세요</p>
            </div>
            <div className="mt-4 space-x-4">
              <Link to={taskType === 'analysis' ? '/analyze' : '/generate'}>
                <Button variant="outline">
                  다시 시도하기
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default ResultsPage
