<script>
    import fastapi from "../lib/api"
    import Error from "../components/Error.svelte"
    import { link, push } from 'svelte-spa-router'
    import { is_login, username } from "../lib/store"
    import { marked } from 'marked'
    import moment from 'moment/min/moment-with-locales'
    moment.locale('ko')

    
    import { onMount } from 'svelte';

    // 댓글 펼치기 상태
    let openComments = {};

    // 댓글 입력 상태
    let newComment = {}; // answer.id별로 댓글 입력값 저장

    // 질문, 답변, 에러 상태
    export let params = {};
    let question_id = params.question_id;
    let question = { answers: [], voter: [], content: '' };
    let content = "";
    let error = { detail: [] };

    // 정렬 방식 상태 추가
    let sortMethod = 'latest';

    // 각 답변별 댓글 관련 상태
    let comments = {}; // 전체 댓글
    let visibleComments = {}; // 화면에 보여지는 댓글
    let commentsToShow = 5; // 한 번에 보여줄 댓글 수
    let commentsContainer = {}; // 댓글 컨테이너 엘리먼트

    // 질문 상태 조회
    function get_question() {
        fastapi("get", "/api/question/detail/" + question_id, {}, (json) => {
            question = json;
            sortMethod = 'latest';
            // 답변별 댓글 상태 초기화
            question.answers.forEach(answer => {
                comments[answer.id] = answer.answer_comments || [];
                visibleComments[answer.id] = comments[answer.id].slice(0, commentsToShow);
            });
        });
    }

    get_question();

    // 답변 정렬 함수
    function sortAnswers(answers, method) {
        return [...answers].sort((a, b) => {
            if (method === 'votes') {
                const voteDiff = b.voter.length - a.voter.length;
                return voteDiff !== 0
                    ? voteDiff
                    : new Date(b.create_date) - new Date(a.create_date);
            } else {
                return new Date(b.create_date) - new Date(a.create_date); // 최신순 정렬
            }
        });
    }

    // 반응형 정렬
    $: sortedAnswers = sortAnswers(question.answers, sortMethod);

    // 답변 등록
    function post_answer(event) {
        event.preventDefault();
        let url = "/api/answer/create/" + question_id;
        let params = {
            content: content
        };
        fastapi('post', url, params,
            (json) => {
                content = '';
                error = { detail: [] };
                get_question();
            },
            (err_json) => {
                error = err_json;
            }
        );
    }

    // 댓글 펼치기
    function toggleComments(answerId) {
        openComments = {
            ...openComments,
            [answerId]: !openComments[answerId]
        };
        // [추가] 펼칠 때 입력값 초기화
        if (openComments[answerId]) {
            newComment[answerId] = '';
        }
    }

    // 댓글 등록
    function addComment(answerId) {
        let commentContent = newComment[answerId];
        if (!commentContent || !commentContent.trim()) return;
        let url = "/api/comment/create/" + answerId;
        let params = { content: commentContent };
        fastapi('post', url, params,
            (json) => {
                newComment[answerId] = '';
                error = { detail: [] };
                get_question();
            },
            (err_json) => {
                error = err_json;
            }
        );
    }

    // 댓글 더 보기
    function loadMoreComments(answerId) {
        const currentVisibleCount = visibleComments[answerId].length;
        const totalComments = comments[answerId].length;

        if (currentVisibleCount < totalComments) {
            const nextComments = comments[answerId].slice(currentVisibleCount, currentVisibleCount + commentsToShow);
            visibleComments[answerId] = [...visibleComments[answerId], ...nextComments];
        }
    }

    // 스크롤 이벤트 핸들러
    function handleScroll(event, answerId) {
        const { scrollTop, scrollHeight, clientHeight } = event.target;
        if (scrollHeight - scrollTop <= clientHeight + 20) { // 20px 전에 로드
            loadMoreComments(answerId);
        }
    }

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

    // 댓글 삭제
    function delete_comment(comment_id) {
        if(window.confirm('정말로 삭제하시겠습니까?')) {
            let url = "/api/comment/delete"
            let params = {
                comment_id: comment_id
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
            <div class="my-3" style="display: flex; gap: 5px;">
                <!-- 질문 추천 버튼 -->    
                <button class="btn btn-sm btn-outline-secondary"
                    on:click="{vote_question(question.id)}"> 
                    추천
                    <span class="badge rounded-pill bg-success">{ question.voter.length }</span>
                </button> 
                

                {#if question.user && $username === question.user.username}
                 <!-- 질문 작성자와 현재 로그인한 사용자가 동일한 경우 -->
                <a use:link href="/question-modify/{question.id}" 
                    class = "btn btn-sm btn-outline-secondary" style="margin-left: auto;">수정</a> <!-- 질문 수정 버튼 활성화 -->
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
    <h5 class="border-bottom my-3 py-2">{question.answers.length}개의 답변이 있습니다.</h5>
    <div class="btn-group">
        <button 
            class="btn btn-sm {sortMethod === 'latest' ? 'btn-primary' : 'btn-outline-secondary'}"
            on:click={() => sortMethod = 'latest'}
        >
            최신순
        </button>
        <button 
            class="btn btn-sm {sortMethod === 'votes' ? 'btn-primary' : 'btn-outline-secondary'}"
            on:click={() => sortMethod = 'votes'}
        >
            추천순
        </button>
    </div>
    {#each sortedAnswers as answer}
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
            <div class="my-3" style="display: flex; gap: 5px;">
                <!-- 답변 추천 버튼 -->
                <button class="btn btn-sm btn-outline-secondary"
                    on:click="{vote_answer(answer.id)}"> 
                    추천
                    <span class="badge rounded-pill bg-success">{ answer.voter.length }</span>
                </button>
                <!--작성된 댓글 펼치기 버튼 -->
                <button class="btn btn-sm btn-outline-secondary"
                    on:click={() => toggleComments(answer.id)}>댓글</button>

                <!-- {#if openComments[answer.id]}
                    <div class="comment-section">
                        {#if answer.comments && answer.comments.length > 0}
                            {#each answer.comments as comment}
                                <div class="comment">
                                    <span class="comment-author">{comment.author}</span>
                                    <span class="comment-content">{comment.content}</span>
                                </div>
                            {/each}
                        {:else}
                            <div class="no-comments">아직 댓글이 없습니다.</div>
                        {/if}
                    </div>
                {/if} -->

                <!-- 답변 수정 및 삭제 버튼 -->
                {#if answer.user && $username === answer.user.username }
                <a use:link href="/answer-modify/{answer.id}" 
                    class="btn btn-sm btn-outline-secondary" style="margin-left: auto;">수정</a>
                <button class="btn btn-sm btn-outline-secondary"
                    on:click={() => delete_answer(answer.id) }>삭제</button>
                {/if}
            </div>
        </div>
        <!-- 댓글창 펼친 후 -->
        {#if openComments[answer.id]}
            <div class="comment-section card mt-2 mx-3 mb-3 p-3">
                <!-- 1. 댓글 작성 폼 -->
                <form on:submit|preventDefault={() => addComment(answer.id)} class="mt-2">
                    <div class="comment input&button d-flex gap-2 mb-3">
                        <input
                            type="text"
                            bind:value={newComment[answer.id]}
                            placeholder="댓글을 입력하세요"
                            class="form-control mb-1"
                            disabled={!$is_login}
                            style="flex: 1 1 auto; min-width: 0;"
                        />
                        <button type="submit" class="btn btn-sm btn-primary" style="white-space: nowrap; min-width: 90px;">댓글 등록</button>
                    </div>
                </form>

                <!-- 2. 댓글 목록 -->
                <div 
                    class="comment-list-container" 
                    style="max-height: 300px; overflow-y: auto;"
                    bind:this={commentsContainer[answer.id]}
                    on:scroll={(e) => handleScroll(e, answer.id)}
                >
                    {#if visibleComments[answer.id] && visibleComments[answer.id].length > 0}
                        {#each visibleComments[answer.id] as comment, i}
                            {#if i > 0}
                                <div class="comment-divider"></div>
                            {/if}
                            <div class="comment" style="display: flex; align-items: center; gap: 10px;">
                                <div class="comment-content ms-2">{comment.content}</div> <!-- 댓글 내용 -->

                                <!-- 댓글 삭제 버튼 -->
                                <div style="margin-left: auto;">
                                    {#if comment.user && $username === comment.user.username }
                                    <button class="btn btn-sm btn-outline-secondary"
                                    on:click={() => delete_comment(comment.id) }>삭제</button>
                                    {/if}
                                </div> 
                                
                                <!--댓글 작성자 및 날짜-->
                                <div class="badge bg-light text-dark p-2 text-start" >
                                    <div class="mb-2">{ comment.user ? comment.user.username : ""}</div> <!-- 댓글 작성자 -->
                                    <div>{moment(comment.create_date).format("YY-MM-DD hh:mm a")}</div> <!-- 댓글 작성 날짜 -->
                                </div>
                            </div>
                        {/each}
                    {:else}
                        <div class="no-comments">아직 댓글이 없습니다.</div>
                    {/if}
                </div>

            </div>
        {/if}

    </div>
    {/each}
    <!-- 답변 등록 -->
    <Error error={error} />
    <form method="post" class="my-3">
        <div class="mb-3">
            <textarea rows="10" bind:value={content} 
                disabled={$is_login ? "" : "disabled"}
                class="form-control" ></textarea>
        </div>
        <input type="submit" value="답변등록" class="btn btn-primary {$is_login ? '' : 'disabled'}" 
            on:click="{post_answer}" />
    </form>
</div>

<!-- 스타일 추가 -->
<style>
    .btn-group > .btn-primary {
        z-index: 1 !important;
        position: relative;
    }

    /* 댓글 구분선 스타일 */
    .comment-divider {
    height: 1px;
    background: rgba(0,0,0,0.15); /* 검정색, 15% 투명도 */
    margin: 0.5rem 0;
    border: none;
}
</style>

