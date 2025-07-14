import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { useToast } from "hooks/use-toast";
import { 
  BookOpen, 
  Loader2, 
  Info, 
  Star,
  Users,
  Clock,
  Target
} from 'lucide-react'

const BookAnalysisPage = () => {
  const navigate = useNavigate()
  const { toast } = useToast()
  
  const [formData, setFormData] = useState({
    title: '',
    author: '',
    ar_level: '',
    pages: '',
    genre: '',
    publication_year: '',
    isbn: '',
    summary: ''
  })
  
  const [isLoading, setIsLoading] = useState(false)

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // 필수 필드 검증
    if (!formData.title || !formData.author || !formData.ar_level) {
      toast({
        title: "입력 오류",
        description: "제목, 저자, AR 레벨은 필수 입력 항목입니다.",
        variant: "destructive"
      })
      return
    }

    setIsLoading(true)

    try {
      const apiUrl = import.meta.env.VITE_API_URL ? `https://${import.meta.env.VITE_API_URL}` : '';
      // API 호출
      const response = await fetch(`${apiUrl}/api/v1/books/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...formData,
          ar_level: parseFloat(formData.ar_level),
          pages: formData.pages ? parseInt(formData.pages) : null,
          publication_year: formData.publication_year ? parseInt(formData.publication_year) : null
        })
      })

      if (!response.ok) {
        throw new Error('분석 요청에 실패했습니다.')
      }

      const result = await response.json()
      
      toast({
        title: "분석 시작됨",
        description: "원서 분석이 시작되었습니다. 결과 페이지로 이동합니다.",
      })

      // 결과 페이지로 이동
      navigate(`/results/${result.task_id}`)

    } catch (error) {
      console.error('Analysis error:', error)
      toast({
        title: "분석 실패",
        description: error.message || "분석 중 오류가 발생했습니다.",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  const sampleBooks = [
    {
      title: "Charlotte's Web",
      author: "E.B. White",
      ar_level: 4.4,
      genre: "Children's Literature"
    },
    {
      title: "The Giver",
      author: "Lois Lowry",
      ar_level: 5.7,
      genre: "Dystopian Fiction"
    },
    {
      title: "Wonder",
      author: "R.J. Palacio",
      ar_level: 4.8,
      genre: "Contemporary Fiction"
    }
  ]

  const fillSampleData = (book) => {
    setFormData(prev => ({
      ...prev,
      title: book.title,
      author: book.author,
      ar_level: book.ar_level.toString(),
      genre: book.genre
    }))
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* 페이지 헤더 */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-2">
          <BookOpen className="h-8 w-8 text-blue-600" />
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
            원서 분석
          </h1>
        </div>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          영어 원서 정보를 입력하면 AI가 자동으로 분석하여 토론 주제와 교육 자료를 생성합니다.
        </p>
      </div>

      {/* 분석 과정 안내 */}
      <Card className="bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-blue-800">
            <Info className="h-5 w-5" />
            <span>분석 과정</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold">
                1
              </div>
              <div>
                <div className="font-semibold text-blue-800">원서 정보 입력</div>
                <div className="text-sm text-blue-600">기본 정보와 요약 입력</div>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold">
                2
              </div>
              <div>
                <div className="font-semibold text-blue-800">AI 분석</div>
                <div className="text-sm text-blue-600">교육 영역별 분석 수행</div>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold">
                3
              </div>
              <div>
                <div className="font-semibold text-blue-800">토론 주제 생성</div>
                <div className="text-sm text-blue-600">레벨별 맞춤 주제 제작</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 메인 폼 */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>원서 정보 입력</CardTitle>
              <CardDescription>
                분석할 영어 원서의 기본 정보를 입력해주세요. 
                제목, 저자, AR 레벨은 필수 항목입니다.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* 필수 정보 */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
                    필수 정보
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="title">제목 *</Label>
                      <Input
                        id="title"
                        value={formData.title}
                        onChange={(e) => handleInputChange('title', e.target.value)}
                        placeholder="예: Charlotte's Web"
                        required
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="author">저자 *</Label>
                      <Input
                        id="author"
                        value={formData.author}
                        onChange={(e) => handleInputChange('author', e.target.value)}
                        placeholder="예: E.B. White"
                        required
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="ar_level">AR 레벨 *</Label>
                      <Input
                        id="ar_level"
                        type="number"
                        step="0.1"
                        min="1.0"
                        max="10.0"
                        value={formData.ar_level}
                        onChange={(e) => handleInputChange('ar_level', e.target.value)}
                        placeholder="예: 4.4"
                        required
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="genre">장르</Label>
                      <Select onValueChange={(value) => handleInputChange('genre', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="장르 선택" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="fiction">Fiction</SelectItem>
                          <SelectItem value="non-fiction">Non-Fiction</SelectItem>
                          <SelectItem value="children">Children's Literature</SelectItem>
                          <SelectItem value="young-adult">Young Adult</SelectItem>
                          <SelectItem value="classic">Classic Literature</SelectItem>
                          <SelectItem value="biography">Biography</SelectItem>
                          <SelectItem value="science">Science</SelectItem>
                          <SelectItem value="history">History</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>

                {/* 선택 정보 */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
                    선택 정보
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="pages">페이지 수</Label>
                      <Input
                        id="pages"
                        type="number"
                        value={formData.pages}
                        onChange={(e) => handleInputChange('pages', e.target.value)}
                        placeholder="예: 184"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="publication_year">출간년도</Label>
                      <Input
                        id="publication_year"
                        type="number"
                        value={formData.publication_year}
                        onChange={(e) => handleInputChange('publication_year', e.target.value)}
                        placeholder="예: 1952"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="isbn">ISBN</Label>
                      <Input
                        id="isbn"
                        value={formData.isbn}
                        onChange={(e) => handleInputChange('isbn', e.target.value)}
                        placeholder="예: 978-0064400558"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="summary">줄거리 요약</Label>
                    <Textarea
                      id="summary"
                      value={formData.summary}
                      onChange={(e) => handleInputChange('summary', e.target.value)}
                      placeholder="원서의 주요 내용과 줄거리를 간단히 요약해주세요. (선택사항)"
                      rows={4}
                    />
                  </div>
                </div>

                <Button 
                  type="submit" 
                  className="w-full bg-blue-600 hover:bg-blue-700"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      분석 중...
                    </>
                  ) : (
                    <>
                      <BookOpen className="h-4 w-4 mr-2" />
                      분석 시작하기
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* 사이드바 */}
        <div className="space-y-6">
          {/* 샘플 도서 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Star className="h-5 w-5 text-yellow-500" />
                <span>샘플 도서</span>
              </CardTitle>
              <CardDescription>
                인기 있는 원서로 빠르게 테스트해보세요
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {sampleBooks.map((book, index) => (
                <div 
                  key={index}
                  className="p-3 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => fillSampleData(book)}
                >
                  <div className="font-semibold text-sm">{book.title}</div>
                  <div className="text-xs text-gray-600">{book.author}</div>
                  <div className="flex items-center justify-between mt-2">
                    <Badge variant="secondary" className="text-xs">
                      AR {book.ar_level}
                    </Badge>
                    <span className="text-xs text-gray-500">{book.genre}</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* 분석 정보 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Target className="h-5 w-5 text-green-500" />
                <span>분석 정보</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-3">
                <Clock className="h-5 w-5 text-blue-500" />
                <div>
                  <div className="font-semibold text-sm">예상 시간</div>
                  <div className="text-xs text-gray-600">2-3분</div>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <Users className="h-5 w-5 text-purple-500" />
                <div>
                  <div className="font-semibold text-sm">생성 주제</div>
                  <div className="text-xs text-gray-600">10-20개</div>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <BookOpen className="h-5 w-5 text-orange-500" />
                <div>
                  <div className="font-semibold text-sm">분석 영역</div>
                  <div className="text-xs text-gray-600">6개 교육 영역</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default BookAnalysisPage
