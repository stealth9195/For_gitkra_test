<script>
    import fastapi from "../lib/api"
    import Error from "../components/Error.svelte"
    import { link, push } from 'svelte-spa-router'
    import { is_login, username } from "../lib/store"
    import { marked } from 'marked'
    import moment from 'moment/min/moment-with-locales'
    moment.locale('ko') // 한국어로 날짜 표시

    export let params = {}
    let question_id = params.question_id
    let question = {answers:[], voter:[], content: ''}
    let content = ""
    let error = {detail:[]}

    function get_question() {
        fastapi("get", "/api/question/detail/" + question_id, {}, (json) => {
            question = json
            
        })
    }

    get_question()

    function post_answer(event) {
        event.preventDefault()
        let url = "/api/answer/create/" + question_id
        let params = {
            content: content
        }
        fastapi('post', url, params, 
            (json) => {
                content = ''
                error = {detail:[]}
                get_question()
            },
            (err_json) => {
                error = err_json
            }
        )
    }

    let answer_list = []
    let size = 5
    let page = 0
    let total = 0
    $: total_page = Math.ceil(total/size)

    // 답변 목록
    function get_answer_list(_page) {
        let params = {
            page: _page,
            size: size,
            question_id: question_id,
        }
        fastapi("get", "/api/answer/list/" , params, (json) => {
            answer_list = json.answer_list
            page = _page
            total = json.total
        })
    }

    get_answer_list(0)

    // 질문 삭제 
    function delete_question(_question_id) {
        if(window.confirm('정말로 삭제하시겠습니까?')) {
            let url = "/api/question/delete"
            let params = {
                question_id: _question_id
            }
            fastapi('delete', url, params, 
                (json) => {
                    push('/')
                },
                (err_json) => {
                    error = err_json
                }
            )
        }
    }

    // 답변 삭제
    function delete_answer(answer_id) {
        if(window.confirm('정말로 삭제하시겠습니까?')) {
            let url = "/api/answer/delete"
            let params = {
                answer_id: answer_id
            }
            fastapi('delete', url, params, 
                (json) => {
                    get_question()
                },
                (err_json) => {
                    error = err_json
                }
            )
        }
    }

    // 질문 추천 기능
    function vote_question(_question_id) {
        if(window.confirm('추천하시겠습니까?')) {
            let url = "/api/question/vote"
            let params = {
                question_id: _question_id
            }
            fastapi('post', url, params, 
                (json) => {
                    get_question()
                },
                (err_json) => {
                    error = err_json
                }
            )
        }
    }

    // 답변 추천 기능
    function vote_answer(answer_id) {
        if(window.confirm('정말로 추천하시겠습니까?')) {
            let url = "/api/answer/vote"
            let params = {
                answer_id: answer_id
            }
            fastapi('post', url, params, 
                (json) => {
                    get_question()
                },
                (err_json) => {
                    error = err_json
                }
            )
        }
    }

</script>

<!-- <h1>{question.subject}</h1>

<div>
    {question.content}
</div>

<ul>
    {#each question.answers as answer}
        <li>{answer.content}</li>
    {/each}
</ul>

<Error error={error} />

<form method="post">
    <textarea rows="15" bind:value={content}></textarea>
    <input type="submit" value="답변등록" on:click="{post_answer}">
</form> -->

<div class="container my-3">
    <!-- 질문 -->
    <h2 class="border-bottom py-2">{question.subject}</h2> <!-- 질문 제목 -->
    <div class="card my-3">
        <div class="card-body">
            <!-- 질문 내용 + 마크다운 -->
            <div class="card-text">
                {@html marked.parse(question.content)}
            </div>
            <div class="d-flex justify-content-end">
                {#if question.modify_date } <!-- 질문 수정 날짜 -->
                <div class="badge bg-light text-dark p-2 text-start mx-3">
                    <div class="mb-2">modified at</div> 
                    <div>{moment(question.modify_date).format("YYYY년 MM월 DD일 hh:mm a")}</div> 
                </div>
                {/if}
                <div class="badge bg-light text-dark p-2 text-start">
                    <div class="mb-2">{ question.user ? question.user.username : ""}</div> <!-- 질문 작성자 -->
                    <div>{moment(question.create_date).format("YYYY년 MM월 DD일 hh:mm a")}</div> <!-- 질문 작성 날짜 -->
                </div>
            </div>
            <div class="my-3">
                <!-- 질문 추천 버튼 -->
                <button class="btn btn-sm btn-outline-secondary"
                    on:click="{vote_question(question.id)}"> 
                    추천
                    <span class="badge rounded-pill bg-success">{ question.voter.length }</span>
                </button> 
                {#if question.user && $username === question.user.username} <!-- 질문 작성자와 현재 로그인한 사용자가 동일한 경우 -->
                <a use:link href="/question-modify/{question.id}" 
                    class = "btn btn-sm btn-outline-secondary">수정</a> <!-- 질문 수정 버튼 활성화 -->
                <button class="btn btn-sm btn-outline-secondary"
                    on:click={() => delete_question(question.id)}>삭제</button> <!-- 질문 삭제 버튼 활성화 -->
                {/if}
            </div>
        </div>
    </div>

    <button class="btn btn-secondary" on:click="{() => {
        push('/')
    }}">목록으로</button>

    <!-- 답변 목록 -->
    <h5 class="border-bottom my-3 py-2">{total}개의 답변이 있습니다.</h5>
    {#each answer_list as answer}
    <div class="card my-3">
        <div class="card-body">
            <!-- 답변 내용 + 마크다운 -->
            <div class="card-text">
                {@html marked.parse(answer.content)}
            </div> 
            <div class="d-flex justify-content-end">
                {#if answer.modify_date }
                <div class="badge bg-light text-dark p-2 text-start mx-3">
                    <div class="mb-2">modified at</div>
                    <div>{moment(answer.modify_date).format("YYYY년 MM월 DD일 hh:mm a")}</div>
                </div>
                {/if}
                <div class="badge bg-light text-dark p-2 text-start">
                    <div class="mb-2">{ answer.user ? answer.user.username : ""}</div>
                    <div>{moment(answer.create_date).format("YYYY년 MM월 DD일 hh:mm a")}</div>
                </div>
            </div>
            <!-- 답변 수정 -->
            <div class="my-3">
                <!-- 답변 추천 버튼 -->
                <button class="btn btn-sm btn-outline-secondary"
                    on:click="{vote_answer(answer.id)}"> 
                    추천
                    <span class="badge rounded-pill bg-success">{ answer.voter.length }</span>
                </button>
                <!-- 답변 수정 및 삭제 버튼 -->
                {#if answer.user && $username === answer.user.username }
                <a use:link href="/answer-modify/{answer.id}" 
                    class="btn btn-sm btn-outline-secondary">수정</a>
                <button class="btn btn-sm btn-outline-secondary"
                    on:click={() => delete_answer(answer.id) }>삭제</button>
                {/if}
            </div>
        </div>
    </div>
    {/each}

    <!-- 페이징처리 시작 -->
    <ul class="pagination justify-content-center">
        <!-- 이전페이지 -->
        <li class="page-item {page <= 0 && 'disabled'}">
            <button class="page-link" on:click="{() => get_answer_list(page-1)}">이전</button>
        </li>
        <!-- 페이지번호 -->
        {#each Array(total_page) as _, loop_page}
        <li class="page-item {loop_page === page && 'active'}">
            <button on:click="{() => get_answer_list(loop_page)}" class="page-link">{loop_page+1}</button>
        </li>
        {/each}
        <!-- 다음페이지 -->
        <li class="page-item {page >= total_page-1 && 'disabled'}">
            <button class="page-link" on:click="{() => get_answer_list(page+1)}">다음</button>
        </li>
    </ul>
    <!-- 페이징처리 끝 -->

    <!-- 답변 등록 -->
    <Error error={error} />
    <form method="post" class="my-3">
        <div class="mb-3">
            <textarea rows="10" bind:value={content} 
                disabled={$is_login ? "" : "disabled"}
                class="form-control" />
        </div>
        <input type="submit" value="답변등록" class="btn btn-primary {$is_login ? '' : 'disabled'}" 
            on:click="{post_answer}" />
    </form>
</div>

