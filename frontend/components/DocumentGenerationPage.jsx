import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { useToast } from "hooks/use-toast";
import { 
  FileText, 
  Upload, 
  Loader2, 
  Download,
  Settings,
  BookOpen,
  Users,
  Target,
  CheckCircle,
  AlertCircle
} from 'lucide-react'

const DocumentGenerationPage = () => {
  const navigate = useNavigate()
  const { toast } = useToast()
  const fileInputRef = useRef(null)
  
  const [csvFile, setCsvFile] = useState(null)
  const [settings, setSettings] = useState({
    title: '파스칼 영어 토론 교재',
    subtitle: 'AI 생성 토론 주제 모음',
    author: '파스칼 교육팀',
    institution: '파스칼 교육원',
    level: 'regular'
  })
  const [isLoading, setIsLoading] = useState(false)
  const [dragOver, setDragOver] = useState(false)

  const handleFileSelect = (file) => {
    if (file && file.type === 'text/csv') {
      setCsvFile(file)
      toast({
        title: "파일 선택됨",
        description: `${file.name} 파일이 선택되었습니다.`
      })
    } else {
      toast({
        title: "파일 형식 오류",
        description: "CSV 파일만 업로드 가능합니다.",
        variant: "destructive"
      })
    }
  }

  const handleFileInputChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setDragOver(false)
  }

  const handleSettingChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!csvFile) {
      toast({
        title: "파일 필요",
        description: "CSV 파일을 먼저 선택해주세요.",
        variant: "destructive"
      })
      return
    }

    setIsLoading(true)

    try {
      const formData = new FormData()
      formData.append('csv_file', csvFile)
      formData.append('settings', JSON.stringify(settings))

      const apiUrl = import.meta.env.VITE_API_URL ? `https://${import.meta.env.VITE_API_URL}` : '';
      const response = await fetch(`${apiUrl}/api/v1/documents/generate`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error('문서 생성 요청에 실패했습니다.')
      }

      const result = await response.json()
      
      toast({
        title: "문서 생성 시작됨",
        description: "DOCX 문서 생성이 시작되었습니다. 결과 페이지로 이동합니다."
      })

      navigate(`/results/${result.task_id}`)

    } catch (error) {
      console.error('Generation error:', error)
      toast({
        title: "생성 실패",
        description: error.message || "문서 생성 중 오류가 발생했습니다.",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  const levelOptions = [
    { value: 'preparation', label: '기초 단계', description: '영어 토론 입문자를 위한 기본 수준' },
    { value: 'regular', label: '발전 단계', description: '중급 수준의 토론 실력 향상' },
    { value: 'mastery', label: '숙달 단계', description: '고급 수준의 독립적 토론 능력' }
  ]

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* 페이지 헤더 */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-2">
          <FileText className="h-8 w-8 text-green-600" />
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
            교재 생성
          </h1>
        </div>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          분석된 CSV 데이터를 업로드하여 완전한 출판 수준의 DOCX 토론 교재를 생성합니다.
        </p>
      </div>

      {/* 생성 과정 안내 */}
      <Card className="bg-green-50 border-green-200">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-green-800">
            <Settings className="h-5 w-5" />
            <span>생성 과정</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3">
              <div className="bg-green-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold">
                1
              </div>
              <div>
                <div className="font-semibold text-green-800">CSV 업로드</div>
                <div className="text-sm text-green-600">분석 결과 CSV 파일 업로드</div>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="bg-green-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold">
                2
              </div>
              <div>
                <div className="font-semibold text-green-800">설정 입력</div>
                <div className="text-sm text-green-600">교재 정보 및 레벨 설정</div>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="bg-green-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold">
                3
              </div>
              <div>
                <div className="font-semibold text-green-800">DOCX 생성</div>
                <div className="text-sm text-green-600">완전한 교재 자동 제작</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 메인 폼 */}
        <div className="lg:col-span-2 space-y-6">
          {/* 파일 업로드 */}
          <Card>
            <CardHeader>
              <CardTitle>CSV 파일 업로드</CardTitle>
              <CardDescription>
                원서 분석 결과 CSV 파일을 업로드해주세요. 
                드래그 앤 드롭 또는 클릭하여 파일을 선택할 수 있습니다.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragOver 
                    ? 'border-green-400 bg-green-50' 
                    : csvFile 
                      ? 'border-green-300 bg-green-50' 
                      : 'border-gray-300 hover:border-gray-400'
                }`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv"
                  onChange={handleFileInputChange}
                  className="hidden"
                />
                
                {csvFile ? (
                  <div className="space-y-3">
                    <CheckCircle className="h-12 w-12 text-green-500 mx-auto" />
                    <div>
                      <div className="font-semibold text-green-800">{csvFile.name}</div>
                      <div className="text-sm text-green-600">
                        {(csvFile.size / 1024).toFixed(1)} KB
                      </div>
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        setCsvFile(null)
                      }}
                    >
                      다른 파일 선택
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <Upload className="h-12 w-12 text-gray-400 mx-auto" />
                    <div>
                      <div className="font-semibold text-gray-700">
                        CSV 파일을 여기에 드롭하거나 클릭하여 선택
                      </div>
                      <div className="text-sm text-gray-500">
                        최대 10MB까지 업로드 가능
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* 교재 설정 */}
          <Card>
            <CardHeader>
              <CardTitle>교재 설정</CardTitle>
              <CardDescription>
                생성할 교재의 기본 정보와 교육 레벨을 설정해주세요.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="title">교재 제목</Label>
                    <Input
                      id="title"
                      value={settings.title}
                      onChange={(e) => handleSettingChange('title', e.target.value)}
                      placeholder="예: 파스칼 영어 토론 교재"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="subtitle">부제목</Label>
                    <Input
                      id="subtitle"
                      value={settings.subtitle}
                      onChange={(e) => handleSettingChange('subtitle', e.target.value)}
                      placeholder="예: Charlotte's Web 기반 토론 학습"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="author">작성자</Label>
                    <Input
                      id="author"
                      value={settings.author}
                      onChange={(e) => handleSettingChange('author', e.target.value)}
                      placeholder="예: 파스칼 교육팀"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="institution">기관명</Label>
                    <Input
                      id="institution"
                      value={settings.institution}
                      onChange={(e) => handleSettingChange('institution', e.target.value)}
                      placeholder="예: 파스칼 교육원"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="level">교육 레벨</Label>
                  <Select 
                    value={settings.level} 
                    onValueChange={(value) => handleSettingChange('level', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="교육 레벨 선택" />
                    </SelectTrigger>
                    <SelectContent>
                      {levelOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          <div className="flex flex-col">
                            <span className="font-semibold">{option.label}</span>
                            <span className="text-xs text-gray-500">{option.description}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <Button 
                  type="submit" 
                  className="w-full bg-green-600 hover:bg-green-700"
                  disabled={isLoading || !csvFile}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      교재 생성 중...
                    </>
                  ) : (
                    <>
                      <FileText className="h-4 w-4 mr-2" />
                      교재 생성하기
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* 사이드바 */}
        <div className="space-y-6">
          {/* 레벨별 특징 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Target className="h-5 w-5 text-blue-500" />
                <span>레벨별 특징</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {levelOptions.map((option) => (
                <div 
                  key={option.value}
                  className={`p-3 border rounded-lg transition-colors ${
                    settings.level === option.value 
                      ? 'border-blue-300 bg-blue-50' 
                      : 'border-gray-200'
                  }`}
                >
                  <div className="font-semibold text-sm">{option.label}</div>
                  <div className="text-xs text-gray-600 mt-1">{option.description}</div>
                  {settings.level === option.value && (
                    <Badge variant="secondary" className="mt-2 text-xs">
                      선택됨
                    </Badge>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>

          {/* 생성 정보 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BookOpen className="h-5 w-5 text-purple-500" />
                <span>생성 정보</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-3">
                <Download className="h-5 w-5 text-green-500" />
                <div>
                  <div className="font-semibold text-sm">출력 형식</div>
                  <div className="text-xs text-gray-600">DOCX (Microsoft Word)</div>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <Users className="h-5 w-5 text-blue-500" />
                <div>
                  <div className="font-semibold text-sm">예상 시간</div>
                  <div className="text-xs text-gray-600">1-2분</div>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <FileText className="h-5 w-5 text-orange-500" />
                <div>
                  <div className="font-semibold text-sm">교재 구성</div>
                  <div className="text-xs text-gray-600">표지, 목차, 챕터, 부록</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 주의사항 */}
          <Card className="border-yellow-200 bg-yellow-50">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-yellow-800">
                <AlertCircle className="h-5 w-5" />
                <span>주의사항</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-yellow-700 space-y-2">
              <p>• CSV 파일은 원서 분석 결과여야 합니다</p>
              <p>• 파일 크기는 10MB를 초과할 수 없습니다</p>
              <p>• 생성된 교재는 24시간 후 자동 삭제됩니다</p>
              <p>• 교재 생성 중에는 페이지를 새로고침하지 마세요</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default DocumentGenerationPage
